from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar


@dataclass(frozen=True, slots=True, kw_only=True)
class EventCommand:
    aggregate_id: str
    actor_id: str
    proposal_id: str | None = None

    event_type: ClassVar[str]
    aggregate_type: ClassVar[str]

    def payload(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("aggregate_id", None)
        data.pop("actor_id", None)
        data.pop("proposal_id", None)
        return data

    def to_event(self) -> dict[str, object]:
        return {
            "event_type": self.event_type,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "payload": self.payload(),
            "actor_id": self.actor_id,
            "proposal_id": self.proposal_id,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class ClaimCreated(EventCommand):
    event_type: ClassVar[str] = "ClaimCreated"
    aggregate_type: ClassVar[str] = "claim"

    statement: str
    claim_type: str
    trust_status: str
    version: int = 1
    context_ids: list[str] = field(default_factory=list)
    context_names: list[str] = field(default_factory=list)
    concept_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    cir_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ClaimUpdated(EventCommand):
    event_type: ClassVar[str] = "ClaimUpdated"
    aggregate_type: ClassVar[str] = "claim"

    changes: dict[str, Any] = field(default_factory=dict)
    version: int = 1


@dataclass(frozen=True, slots=True, kw_only=True)
class ClaimTrustChanged(EventCommand):
    event_type: ClassVar[str] = "ClaimTrustChanged"
    aggregate_type: ClassVar[str] = "claim"

    previous_status: str
    new_status: str
    reason: str | None = None
    version: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ClaimRetracted(EventCommand):
    event_type: ClassVar[str] = "ClaimRetracted"
    aggregate_type: ClassVar[str] = "claim"

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ConceptCreated(EventCommand):
    event_type: ClassVar[str] = "ConceptCreated"
    aggregate_type: ClassVar[str] = "concept"

    label: str
    description: str
    domain_field: str
    term_ids: list[str] = field(default_factory=list)
    referent_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ConceptUpdated(EventCommand):
    event_type: ClassVar[str] = "ConceptUpdated"
    aggregate_type: ClassVar[str] = "concept"

    changes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class ConceptLinkedToClaim(EventCommand):
    event_type: ClassVar[str] = "ConceptLinkedToClaim"
    aggregate_type: ClassVar[str] = "concept"

    claim_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceCreated(EventCommand):
    event_type: ClassVar[str] = "EvidenceCreated"
    aggregate_type: ClassVar[str] = "evidence"

    evidence_type: str
    title: str
    source: str
    reliability: str
    excerpt: str | None = None
    claim_links: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceLinkedToClaim(EventCommand):
    event_type: ClassVar[str] = "EvidenceLinkedToClaim"
    aggregate_type: ClassVar[str] = "evidence"

    claim_id: str
    relationship: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextCreated(EventCommand):
    event_type: ClassVar[str] = "ContextCreated"
    aggregate_type: ClassVar[str] = "context"

    name: str
    description: str
    domain_field: str
    assumptions: list[str] = field(default_factory=list)
    parent_context_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextUpdated(EventCommand):
    event_type: ClassVar[str] = "ContextUpdated"
    aggregate_type: ClassVar[str] = "context"

    changes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProposalCreated(EventCommand):
    event_type: ClassVar[str] = "ProposalCreated"
    aggregate_type: ClassVar[str] = "proposal"

    proposal_type: str
    target_entity_type: str
    target_entity_id: str | None = None
    payload_data: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    status: str = "pending"

    def payload(self) -> dict[str, Any]:
        data = super().payload()
        data["payload"] = data.pop("payload_data")
        return data


@dataclass(frozen=True, slots=True, kw_only=True)
class ProposalApproved(EventCommand):
    event_type: ClassVar[str] = "ProposalApproved"
    aggregate_type: ClassVar[str] = "proposal"

    review_id: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ProposalRejected(EventCommand):
    event_type: ClassVar[str] = "ProposalRejected"
    aggregate_type: ClassVar[str] = "proposal"

    review_id: str | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class CrossFieldLinkProposed(EventCommand):
    event_type: ClassVar[str] = "CrossFieldLinkProposed"
    aggregate_type: ClassVar[str] = "cross_field_connection"

    source_claim_id: str
    target_claim_id: str
    connection_type: str
    description: str
    confidence: float
    status: str = "pending"


@dataclass(frozen=True, slots=True, kw_only=True)
class CrossFieldLinkApproved(EventCommand):
    event_type: ClassVar[str] = "CrossFieldLinkApproved"
    aggregate_type: ClassVar[str] = "cross_field_connection"

    notes: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class CrossFieldLinkRejected(EventCommand):
    event_type: ClassVar[str] = "CrossFieldLinkRejected"
    aggregate_type: ClassVar[str] = "cross_field_connection"

    reason: str | None = None


EVENT_COMMANDS = (
    ClaimCreated,
    ClaimUpdated,
    ClaimTrustChanged,
    ClaimRetracted,
    ConceptCreated,
    ConceptUpdated,
    ConceptLinkedToClaim,
    EvidenceCreated,
    EvidenceLinkedToClaim,
    ContextCreated,
    ContextUpdated,
    ProposalCreated,
    ProposalApproved,
    ProposalRejected,
    CrossFieldLinkProposed,
    CrossFieldLinkApproved,
    CrossFieldLinkRejected,
)
