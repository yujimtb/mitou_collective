from __future__ import annotations

from pydantic import Field

from app.schemas.actor import ActorRef
from app.schemas.common import ProposalStatus, ProposalType, SchemaModel, TimestampedRead


class ProposalCreate(SchemaModel):
    proposal_type: ProposalType
    target_entity_type: str = Field(min_length=1, max_length=50)
    target_entity_id: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)
    rationale: str = Field(min_length=1)


class ProposalUpdate(SchemaModel):
    payload: dict[str, object] | None = None
    rationale: str | None = None
    status: ProposalStatus | None = None


class ProposalRead(TimestampedRead):
    proposal_type: ProposalType
    proposed_by: ActorRef
    target_entity_type: str
    target_entity_id: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)
    rationale: str
    status: ProposalStatus
    reviewed_at: str | None = None
    reviewed_by: ActorRef | None = None
