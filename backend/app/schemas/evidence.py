from __future__ import annotations

from pydantic import Field

from app.schemas.actor import ActorRef
from app.schemas.common import EvidenceRelationship, EvidenceType, Reliability, SchemaModel, TimestampedRead


class ClaimEvidenceLink(SchemaModel):
    claim_id: str
    relationship: EvidenceRelationship = EvidenceRelationship.SUPPORTS


class EvidenceCreate(SchemaModel):
    evidence_type: EvidenceType
    title: str = Field(min_length=1, max_length=500)
    source: str = Field(min_length=1)
    excerpt: str | None = None
    reliability: Reliability = Reliability.UNVERIFIED
    claim_links: list[ClaimEvidenceLink] = Field(default_factory=list)


class EvidenceUpdate(SchemaModel):
    evidence_type: EvidenceType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=500)
    source: str | None = None
    excerpt: str | None = None
    reliability: Reliability | None = None
    claim_links: list[ClaimEvidenceLink] | None = None


class EvidenceRead(TimestampedRead):
    evidence_type: EvidenceType
    title: str
    source: str
    excerpt: str | None = None
    reliability: Reliability
    claim_links: list[ClaimEvidenceLink] = Field(default_factory=list)
    created_by: ActorRef | None = None
