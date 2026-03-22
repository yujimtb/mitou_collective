from __future__ import annotations

from datetime import datetime, UTC

from app.interfaces import IClaimService, IConceptService, IProposalService
from app.schemas import (
    ActorRef,
    ActorType,
    ClaimRead,
    ClaimType,
    ConceptRead,
    ConnectionType,
    ContextRead,
    EvidenceRead,
    EvidenceType,
    PaginatedResponse,
    ProposalCreate,
    ProposalRead,
    ProposalStatus,
    ProposalType,
    Reliability,
    TermRead,
    TrustLevel,
    TrustStatus,
)

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def make_actor(
    actor_id: str, *, name: str = "Agent", actor_type: ActorType = ActorType.AI_AGENT
) -> ActorRef:
    return ActorRef(
        id=actor_id,
        actor_type=actor_type,
        name=name,
        trust_level=TrustLevel.REVIEWER,
        agent_model="gpt-5.4" if actor_type is ActorType.AI_AGENT else None,
    )


def make_claim(
    claim_id: str,
    *,
    statement: str,
    concept_ids: list[str],
    context_ids: list[str] | None = None,
    evidence_ids: list[str] | None = None,
) -> ClaimRead:
    return ClaimRead(
        id=claim_id,
        created_at=NOW,
        statement=statement,
        claim_type=ClaimType.THEOREM,
        trust_status=TrustStatus.TENTATIVE,
        context_ids=context_ids or [],
        concept_ids=concept_ids,
        evidence_ids=evidence_ids or [],
        cir=None,
        created_by=None,
        version=1,
    )


def make_concept(
    concept_id: str, *, label: str, description: str, field: str, term_ids: list[str] | None = None
) -> ConceptRead:
    return ConceptRead(
        id=concept_id,
        created_at=NOW,
        label=label,
        description=description,
        field=field,
        term_ids=term_ids or [],
        referent_id=None,
        created_by=None,
    )


def make_context(
    context_id: str, *, name: str, field: str, assumptions: list[str] | None = None
) -> ContextRead:
    return ContextRead(
        id=context_id,
        created_at=NOW,
        name=name,
        description=f"{name} description",
        field=field,
        assumptions=assumptions or [],
        parent_context_id=None,
        created_by=None,
    )


def make_evidence(evidence_id: str, *, title: str, excerpt: str | None = None) -> EvidenceRead:
    return EvidenceRead(
        id=evidence_id,
        created_at=NOW,
        evidence_type=EvidenceType.PAPER,
        title=title,
        source="source",
        excerpt=excerpt,
        reliability=Reliability.HIGH,
        claim_links=[],
        created_by=None,
    )


def make_term(term_id: str, *, surface_form: str, concept_ids: list[str] | None = None) -> TermRead:
    return TermRead(
        id=term_id,
        created_at=NOW,
        surface_form=surface_form,
        language="en",
        field_hint=None,
        concept_ids=concept_ids or [],
        created_by=None,
    )


def make_proposal(
    proposal_id: str,
    *,
    actor: ActorRef,
    payload: dict[str, object],
    rationale: str = "generated rationale",
    status: ProposalStatus = ProposalStatus.PENDING,
) -> ProposalRead:
    return ProposalRead(
        id=proposal_id,
        created_at=NOW,
        proposal_type=ProposalType.CONNECT_CONCEPTS,
        proposed_by=actor,
        target_entity_type="claim" if "target_claim_id" in payload else "concept",
        target_entity_id=str(
            payload.get("target_claim_id") or payload.get("target_concept_id") or ""
        ),
        payload=payload,
        rationale=rationale,
        status=status,
        reviewed_at=None,
        reviewed_by=None,
    )


class InMemoryClaimService(IClaimService):
    def __init__(self, claims: list[ClaimRead]):
        self._claims = {claim.id: claim for claim in claims}

    async def create(
        self, payload, actor_id: str
    ) -> ClaimRead:  # pragma: no cover - unused in Track F tests
        raise NotImplementedError

    async def get(self, claim_id: str) -> ClaimRead:
        return self._claims[claim_id]

    async def list(
        self, *, page: int = 1, per_page: int = 20, **filters: object
    ) -> PaginatedResponse[ClaimRead]:
        claims = list(self._claims.values())
        return PaginatedResponse[ClaimRead](
            total_count=len(claims),
            current_page=page,
            per_page=per_page,
            items=claims[:per_page],
        )

    async def update(
        self, claim_id: str, payload, actor_id: str
    ) -> ClaimRead:  # pragma: no cover - unused
        raise NotImplementedError

    async def history(self, claim_id: str) -> list[dict[str, object]]:  # pragma: no cover - unused
        raise NotImplementedError

    async def history_formatted(self, claim_id: str) -> list[dict[str, object]]:  # pragma: no cover - unused
        raise NotImplementedError

    async def retract(self, claim_id: str, actor_id: str):  # pragma: no cover - unused
        raise NotImplementedError


class InMemoryConceptService(IConceptService):
    def __init__(self, concepts: list[ConceptRead]):
        self._concepts = {concept.id: concept for concept in concepts}

    async def create(self, payload, actor_id: str) -> ConceptRead:  # pragma: no cover - unused
        raise NotImplementedError

    async def get(self, concept_id: str) -> ConceptRead:
        return self._concepts[concept_id]

    async def list(
        self, *, page: int = 1, per_page: int = 20, **filters: object
    ) -> PaginatedResponse[ConceptRead]:
        concepts = list(self._concepts.values())
        return PaginatedResponse[ConceptRead](
            total_count=len(concepts),
            current_page=page,
            per_page=per_page,
            items=concepts[:per_page],
        )

    async def update(
        self, concept_id: str, payload, actor_id: str
    ) -> ConceptRead:  # pragma: no cover - unused
        raise NotImplementedError

    async def connections(self, concept_id: str):  # pragma: no cover - unused
        raise NotImplementedError


class InMemoryProposalService(IProposalService):
    def __init__(self, *, actors: dict[str, ActorRef], existing: list[ProposalRead] | None = None):
        self._actors = actors
        self._items = list(existing or [])

    async def create(self, payload: ProposalCreate, actor_id: str) -> ProposalRead:
        proposal = ProposalRead(
            id=f"proposal-{len(self._items) + 1}",
            created_at=NOW,
            proposal_type=payload.proposal_type,
            proposed_by=self._actors[actor_id],
            target_entity_type=payload.target_entity_type,
            target_entity_id=payload.target_entity_id,
            payload=payload.payload,
            rationale=payload.rationale,
            status=ProposalStatus.PENDING,
            reviewed_at=None,
            reviewed_by=None,
        )
        self._items.append(proposal)
        return proposal

    async def get(self, proposal_id: str) -> ProposalRead:
        return next(item for item in self._items if item.id == proposal_id)

    async def list(
        self, *, page: int = 1, per_page: int = 20, **filters: object
    ) -> PaginatedResponse[ProposalRead]:
        items = self._items
        proposal_type = filters.get("proposal_type")
        if proposal_type is not None:
            items = [item for item in items if item.proposal_type == proposal_type]
        return PaginatedResponse[ProposalRead](
            total_count=len(items),
            current_page=page,
            per_page=per_page,
            items=items[:per_page],
        )

    async def update(
        self, proposal_id: str, payload, actor_id: str
    ) -> ProposalRead:  # pragma: no cover - unused
        raise NotImplementedError


DEFAULT_AI_ACTOR = make_actor("ai-1")
DEFAULT_HUMAN_ACTOR = make_actor("user-1", name="User", actor_type=ActorType.HUMAN)


def make_claim_candidate(
    *,
    source_claim_id: str,
    target_claim_id: str,
    confidence: float,
    rationale: str = "The structures align across fields.",
    connection_type: ConnectionType = ConnectionType.ANALOGOUS,
) -> dict[str, object]:
    return {
        "source_claim_id": source_claim_id,
        "target_claim_id": target_claim_id,
        "connection_type": connection_type.value,
        "confidence": confidence,
        "rationale": rationale,
        "caveats": [],
    }
