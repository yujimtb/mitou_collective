from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class StrEnum(str, Enum):
    pass


class ClaimType(StrEnum):
    DEFINITION = "definition"
    THEOREM = "theorem"
    EMPIRICAL = "empirical"
    CONJECTURE = "conjecture"
    META = "meta"


class TrustStatus(StrEnum):
    ESTABLISHED = "established"
    TENTATIVE = "tentative"
    DISPUTED = "disputed"
    AI_SUGGESTED = "ai_suggested"
    RETRACTED = "retracted"


class EvidenceType(StrEnum):
    TEXTBOOK = "textbook"
    PAPER = "paper"
    EXPERIMENT = "experiment"
    PROOF = "proof"
    EXPERT_OPINION = "expert_opinion"


class Reliability(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"


class ProposalType(StrEnum):
    CREATE_CLAIM = "create_claim"
    LINK_CLAIMS = "link_claims"
    UPDATE_TRUST = "update_trust"
    ADD_EVIDENCE = "add_evidence"
    CONNECT_CONCEPTS = "connect_concepts"


class ProposalStatus(StrEnum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ReviewDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"


class ConnectionType(StrEnum):
    EQUIVALENT = "equivalent"
    ANALOGOUS = "analogous"
    GENERALIZES = "generalizes"
    CONTRADICTS = "contradicts"
    COMPLEMENTS = "complements"


class ActorType(StrEnum):
    HUMAN = "human"
    AI_AGENT = "ai_agent"


class TrustLevel(StrEnum):
    ADMIN = "admin"
    REVIEWER = "reviewer"
    CONTRIBUTOR = "contributor"
    OBSERVER = "observer"


class EvidenceRelationship(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    PARTIALLY_SUPPORTS = "partially_supports"


class AutonomyLevel(StrEnum):
    LEVEL_0 = "level_0"
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"


class SchemaModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class TimestampedRead(SchemaModel):
    id: str
    created_at: datetime


class ErrorDetail(SchemaModel):
    code: str
    message: str
    details: dict[str, object] = Field(default_factory=dict)


class ErrorResponse(SchemaModel):
    error: ErrorDetail


ItemT = TypeVar("ItemT")


class PaginatedResponse(SchemaModel, Generic[ItemT]):
    total_count: int = Field(ge=0)
    current_page: int = Field(ge=1)
    per_page: int = Field(ge=1, le=100)
    items: list[ItemT]
