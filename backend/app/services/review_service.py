from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.policy_engine import PolicyEngine
from app.interfaces import IEventStore, IReviewService
from app.models import Actor, Proposal, Review
from app.schemas import ActorRead, ActorRef, ReviewCreate, ReviewDecision, ReviewRead
from app.workflows import ChangeApplier, PendingEvent, ProposalStateMachine


SessionFactory = Callable[[], Session]


class ReviewService(IReviewService):
    def __init__(
        self,
        session_factory: SessionFactory,
        event_store: IEventStore,
        *,
        policy_engine: PolicyEngine | None = None,
        state_machine: ProposalStateMachine | None = None,
        change_applier: ChangeApplier | None = None,
    ):
        self._session_factory = session_factory
        self._event_store = event_store
        self._policy_engine = policy_engine or PolicyEngine()
        self._state_machine = state_machine or ProposalStateMachine()
        self._change_applier = change_applier or ChangeApplier()

    async def create(self, payload: ReviewCreate, actor_id: str) -> ReviewRead:
        proposal_uuid = self._parse_uuid(payload.proposal_id, field_name="proposal_id")
        actor_uuid = self._parse_uuid(actor_id, field_name="actor_id")

        pending_events: list[PendingEvent] = []
        with self._session_factory() as session:
            reviewer = self._require_actor(session, actor_uuid)
            proposal = session.get(Proposal, proposal_uuid)
            if proposal is None:
                raise LookupError(f"proposal '{payload.proposal_id}' not found")

            risk = self._state_machine.classify_risk(proposal.proposal_type)
            self._policy_engine.assert_can_review_proposal(
                self._actor_to_read(reviewer),
                proposal_author_id=str(proposal.proposed_by_id),
                risk=risk,
            )

            proposal.status = self._state_machine.apply_review(proposal.status, payload.decision)
            review = Review(
                proposal_id=proposal.id,
                reviewer_id=reviewer.id,
                decision=payload.decision,
                comment=payload.comment,
                confidence=payload.confidence,
            )
            session.add(review)
            session.flush()

            if payload.decision is ReviewDecision.APPROVE:
                proposal.reviewed_at = datetime.now(UTC)
                proposal.reviewed_by_id = reviewer.id
                pending_events.append(
                    PendingEvent(
                        event_type="ProposalApproved",
                        aggregate_type="proposal",
                        aggregate_id=str(proposal.id),
                        payload={
                            "review_id": str(review.id),
                            "notes": payload.comment,
                        },
                        actor_id=actor_id,
                        proposal_id=str(proposal.id),
                    )
                )
                applied = self._change_applier.apply(session, proposal, actor_id=actor_id)
                pending_events.extend(applied.events)
            elif payload.decision is ReviewDecision.REJECT:
                proposal.reviewed_at = datetime.now(UTC)
                proposal.reviewed_by_id = reviewer.id
                pending_events.append(
                    PendingEvent(
                        event_type="ProposalRejected",
                        aggregate_type="proposal",
                        aggregate_id=str(proposal.id),
                        payload={
                            "review_id": str(review.id),
                            "reason": payload.comment,
                        },
                        actor_id=actor_id,
                        proposal_id=str(proposal.id),
                    )
                )

            session.add(proposal)
            session.commit()
            session.refresh(review)

            result = self._to_schema(review)

        for event in pending_events:
            await self._event_store.append(
                event_type=event.event_type,
                aggregate_type=event.aggregate_type,
                aggregate_id=event.aggregate_id,
                payload=event.payload,
                actor_id=event.actor_id,
                proposal_id=event.proposal_id,
            )

        return result

    async def list_for_proposal(self, proposal_id: str) -> list[ReviewRead]:
        proposal_uuid = self._parse_uuid(proposal_id, field_name="proposal_id")
        statement = (
            select(Review)
            .where(Review.proposal_id == proposal_uuid)
            .order_by(Review.created_at.asc())
        )
        with self._session_factory() as session:
            reviews = session.scalars(statement).all()
            return [self._to_schema(review) for review in reviews]

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
    def _actor_to_ref(actor: Actor) -> ActorRef:
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
    def _to_schema(cls, review: Review) -> ReviewRead:
        return ReviewRead(
            id=str(review.id),
            proposal_id=str(review.proposal_id),
            reviewer=cls._actor_to_ref(review.reviewer),
            decision=review.decision,
            comment=review.comment,
            confidence=review.confidence,
            created_at=review.created_at,
        )
