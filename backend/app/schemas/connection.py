from __future__ import annotations

from pydantic import Field

from app.schemas.common import ConnectionType, ProposalStatus, SchemaModel, TimestampedRead


class CrossFieldConnectionCreate(SchemaModel):
    source_claim_id: str
    target_claim_id: str
    connection_type: ConnectionType
    description: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    proposal_id: str | None = None


class CrossFieldConnectionUpdate(SchemaModel):
    connection_type: ConnectionType | None = None
    description: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    proposal_id: str | None = None
    status: ProposalStatus | None = None


class CrossFieldConnectionRead(TimestampedRead):
    source_claim_id: str
    target_claim_id: str
    connection_type: ConnectionType
    description: str
    confidence: float
    proposal_id: str | None = None
    status: ProposalStatus = ProposalStatus.PENDING
