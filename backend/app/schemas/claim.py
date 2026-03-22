from __future__ import annotations

from pydantic import Field

from app.schemas.actor import ActorRef
from app.schemas.cir import CIRRead
from app.schemas.common import ClaimType, SchemaModel, TimestampedRead, TrustStatus


class ClaimCreate(SchemaModel):
    statement: str = Field(min_length=1)
    claim_type: ClaimType
    trust_status: TrustStatus = TrustStatus.TENTATIVE
    context_ids: list[str] = Field(default_factory=list)
    concept_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    cir_id: str | None = None


class ClaimUpdate(SchemaModel):
    statement: str | None = None
    claim_type: ClaimType | None = None
    trust_status: TrustStatus | None = None
    context_ids: list[str] | None = None
    concept_ids: list[str] | None = None
    evidence_ids: list[str] | None = None
    cir_id: str | None = None


class ClaimRead(TimestampedRead):
    statement: str
    claim_type: ClaimType
    trust_status: TrustStatus
    context_ids: list[str] = Field(default_factory=list)
    concept_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    cir: CIRRead | None = None
    created_by: ActorRef | None = None
    version: int = Field(default=1, ge=1)
