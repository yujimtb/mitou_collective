from __future__ import annotations

from collections.abc import Callable
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.policy_engine import Operation, PolicyEngine
from app.interfaces import IEventStore, IProposalService
from app.models import Actor, Proposal
from app.schemas import (
    ActorRead,
    ActorRef,
    PaginatedResponse,
    ProposalCreate,
    ProposalRead,
    ProposalStatus,
    ProposalUpdate,
)
from app.workflows import ProposalStateMachine


SessionFactory = Callable[[], Session]


class ProposalService(IProposalService):
    def __init__(
        self,
        session_factory: SessionFactory,
        event_store: IEventStore,
        *,
        policy_engine: PolicyEngine | None = None,
        state_machine: ProposalStateMachine | None = None,
    ):
        self._session_factory = session_factory
        self._event_store = event_store
        self._policy_engine = policy_engine or PolicyEngine()
        self._state_machine = state_machine or ProposalStateMachine()

    async def create(self, payload: ProposalCreate, actor_id: str) -> ProposalRead:
        actor_uuid = self._parse_uuid(actor_id, field_name="actor_id")
        with self._session_factory() as session:
            actor = self._require_actor(session, actor_uuid)
            self._policy_engine.assert_allowed(
                self._actor_to_read(actor), Operation.CREATE_PROPOSAL
            )

            proposal = Proposal(
                proposal_type=payload.proposal_type,
                proposed_by_id=actor.id,
                target_entity_type=payload.target_entity_type,
                target_entity_id=self._optional_uuid(payload.target_entity_id),
                payload=payload.payload,
                rationale=payload.rationale,
                status=ProposalStatus.PENDING,
            )
            session.add(proposal)
            session.flush()
            session.refresh(proposal)

            result = self._to_schema(proposal)

            await self._event_store.append(
                event_type="ProposalCreated",
                aggregate_type="proposal",
                aggregate_id=result.id,
                payload={
                    "proposal_type": result.proposal_type.value,
                    "target_entity_type": result.target_entity_type,
                    "target_entity_id": result.target_entity_id,
                    "payload": result.payload,
                    "rationale": result.rationale,
                    "status": result.status.value,
                },
                actor_id=actor_id,
                session=session,
            )
            session.commit()
        return result

    async def get(self, proposal_id: str) -> ProposalRead:
        proposal_uuid = self._parse_uuid(proposal_id, field_name="proposal_id")
        with self._session_factory() as session:
            proposal = session.get(Proposal, proposal_uuid)
            if proposal is None:
                raise LookupError(f"proposal '{proposal_id}' not found")
            return self._to_schema(proposal)

    async def list(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        **filters: object,
    ) -> PaginatedResponse[ProposalRead]:
        if page < 1:
            raise ValueError("page must be at least 1")
        if per_page < 1 or per_page > 100:
            raise ValueError("per_page must be between 1 and 100")

        statement = select(Proposal).order_by(Proposal.created_at.asc())
        count_statement = select(func.count()).select_from(Proposal)

        if status := filters.get("status"):
            statement = statement.where(Proposal.status == status)
            count_statement = count_statement.where(Proposal.status == status)
        if proposal_type := filters.get("proposal_type"):
            statement = statement.where(Proposal.proposal_type == proposal_type)
            count_statement = count_statement.where(Proposal.proposal_type == proposal_type)
        if target_entity_type := filters.get("target_entity_type"):
            statement = statement.where(Proposal.target_entity_type == target_entity_type)
            count_statement = count_statement.where(
                Proposal.target_entity_type == target_entity_type
            )
        if proposed_by_id := filters.get("proposed_by_id"):
            statement = statement.where(
                Proposal.proposed_by_id
                == self._parse_uuid(proposed_by_id, field_name="proposed_by_id")
            )
            count_statement = count_statement.where(
                Proposal.proposed_by_id
                == self._parse_uuid(proposed_by_id, field_name="proposed_by_id")
            )

        statement = statement.offset((page - 1) * per_page).limit(per_page)

        with self._session_factory() as session:
            total_count = session.scalar(count_statement) or 0
            proposals = session.scalars(statement).all()
            return PaginatedResponse[ProposalRead](
                total_count=total_count,
                current_page=page,
                per_page=per_page,
                items=[self._to_schema(proposal) for proposal in proposals],
            )

    async def update(
        self, proposal_id: str, payload: ProposalUpdate, actor_id: str
    ) -> ProposalRead:
        proposal_uuid = self._parse_uuid(proposal_id, field_name="proposal_id")
        actor_uuid = self._parse_uuid(actor_id, field_name="actor_id")

        with self._session_factory() as session:
            actor = self._require_actor(session, actor_uuid)
            proposal = session.get(Proposal, proposal_uuid)
            if proposal is None:
                raise LookupError(f"proposal '{proposal_id}' not found")

            updates = payload.model_dump(exclude_unset=True)
            requested_status = updates.pop("status", None)

            if requested_status is not None:
                if requested_status is not ProposalStatus.WITHDRAWN:
                    raise ValueError(
                        "proposal status can only be changed to withdrawn via ProposalService"
                    )
                if actor.id != proposal.proposed_by_id:
                    raise PermissionError("only the proposal author can withdraw a proposal")
                proposal.status = self._state_machine.withdraw(proposal.status)

            if updates:
                if actor.id != proposal.proposed_by_id:
                    self._policy_engine.assert_allowed(self._actor_to_read(actor), Operation.WRITE)
                self._state_machine.assert_editable(proposal.status)
                if "payload" in updates:
                    proposal.payload = updates["payload"]
                if "rationale" in updates and updates["rationale"] is not None:
                    proposal.rationale = updates["rationale"]

            session.add(proposal)
            session.commit()
            session.refresh(proposal)
            return self._to_schema(proposal)

    @staticmethod
    def _require_actor(session: Session, actor_id: uuid.UUID) -> Actor:
        actor = session.get(Actor, actor_id)
        if actor is None:
            raise LookupError(f"actor '{actor_id}' not found")
        return actor

    @staticmethod
    def _parse_uuid(raw_value: str, *, field_name: str) -> uuid.UUID:
        try:
            return uuid.UUID(raw_value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid UUID") from exc

    @staticmethod
    def _optional_uuid(raw_value: str | None) -> uuid.UUID | None:
        if raw_value is None:
            return None
        return uuid.UUID(raw_value)

    @staticmethod
    def _actor_to_ref(actor: Actor | None) -> ActorRef | None:
        if actor is None:
            return None
        return ActorRef(
            id=str(actor.id),
            actor_type=actor.actor_type,
            name=actor.name,
            trust_level=actor.trust_level,
            agent_model=actor.agent_model,
        )

    @classmethod
    def _actor_to_read(cls, actor: Actor) -> ActorRead:
        return ActorRead(
            id=str(actor.id),
            actor_type=actor.actor_type,
            name=actor.name,
            trust_level=actor.trust_level,
            agent_model=actor.agent_model,
            created_at=actor.created_at,
        )

    @classmethod
    def _to_schema(cls, proposal: Proposal) -> ProposalRead:
        return ProposalRead(
            id=str(proposal.id),
            proposal_type=proposal.proposal_type,
            proposed_by=cls._actor_to_ref(proposal.proposed_by),
            target_entity_type=proposal.target_entity_type,
            target_entity_id=str(proposal.target_entity_id) if proposal.target_entity_id else None,
            payload=dict(proposal.payload),
            rationale=proposal.rationale,
            status=proposal.status,
            created_at=proposal.created_at,
            reviewed_at=proposal.reviewed_at,
            reviewed_by=cls._actor_to_ref(proposal.reviewed_by),
        )
