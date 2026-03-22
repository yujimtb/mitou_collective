from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import uuid

from sqlalchemy.orm import Session

from app.models import (
    Claim,
    ClaimConcept,
    ClaimContext,
    ClaimEvidence,
    Concept,
    Context,
    CrossFieldConnection,
    Evidence,
    Proposal,
)
from app.schemas import (
    ClaimType,
    ConnectionType,
    EvidenceRelationship,
    EvidenceType,
    ProposalStatus,
    ProposalType,
    Reliability,
    TrustStatus,
)
from app.workflows.trust_transitions import TrustTransitionEngine, TrustTransitionRequest


@dataclass(frozen=True, slots=True)
class PendingEvent:
    event_type: str
    aggregate_type: str
    aggregate_id: str
    payload: dict[str, object]
    actor_id: str
    proposal_id: str | None = None


@dataclass(frozen=True, slots=True)
class AppliedProposalChange:
    events: list[PendingEvent] = field(default_factory=list)
    entity_ids: dict[str, str] = field(default_factory=dict)


class ChangeApplier:
    def __init__(self, *, trust_engine: TrustTransitionEngine | None = None):
        self._trust_engine = trust_engine or TrustTransitionEngine()

    def apply(
        self, session: Session, proposal: Proposal, *, actor_id: str
    ) -> AppliedProposalChange:
        if proposal.proposal_type is ProposalType.CREATE_CLAIM:
            return self._apply_create_claim(session, proposal, actor_id=actor_id)
        if proposal.proposal_type in {ProposalType.LINK_CLAIMS, ProposalType.CONNECT_CONCEPTS}:
            return self._apply_connection(session, proposal, actor_id=actor_id)
        if proposal.proposal_type is ProposalType.UPDATE_TRUST:
            return self._apply_trust_update(session, proposal, actor_id=actor_id)
        if proposal.proposal_type is ProposalType.ADD_EVIDENCE:
            return self._apply_add_evidence(session, proposal, actor_id=actor_id)
        raise ValueError(f"unsupported proposal type '{proposal.proposal_type.value}'")

    def _apply_create_claim(
        self,
        session: Session,
        proposal: Proposal,
        *,
        actor_id: str,
    ) -> AppliedProposalChange:
        payload = proposal.payload
        trust_status = TrustStatus(payload.get("trust_status", TrustStatus.TENTATIVE.value))
        trust_status = self._trust_engine.approve_claim(trust_status)

        claim = Claim(
            statement=self._require_str(payload, "statement"),
            claim_type=ClaimType(self._require_str(payload, "claim_type")),
            trust_status=trust_status,
            created_by_id=proposal.proposed_by_id,
        )
        session.add(claim)
        session.flush()

        context_ids = [
            self._parse_uuid(item, field_name="context_ids")
            for item in payload.get("context_ids", [])
        ]
        concept_ids = [
            self._parse_uuid(item, field_name="concept_ids")
            for item in payload.get("concept_ids", [])
        ]

        context_names: list[str] = []
        for context_id in context_ids:
            context = session.get(Context, context_id)
            if context is None:
                raise LookupError(f"context '{context_id}' not found")
            context_names.append(context.name)
            session.add(ClaimContext(claim_id=claim.id, context_id=context_id))

        for concept_id in concept_ids:
            concept = session.get(Concept, concept_id)
            if concept is None:
                raise LookupError(f"concept '{concept_id}' not found")
            session.add(ClaimConcept(claim_id=claim.id, concept_id=concept_id))

        event = PendingEvent(
            event_type="ClaimCreated",
            aggregate_type="claim",
            aggregate_id=str(claim.id),
            payload={
                "statement": claim.statement,
                "claim_type": claim.claim_type.value,
                "trust_status": claim.trust_status.value,
                "version": claim.version,
                "context_ids": [str(item) for item in context_ids],
                "context_names": context_names,
                "concept_ids": [str(item) for item in concept_ids],
                "evidence_ids": [],
                "cir_id": None,
            },
            actor_id=actor_id,
            proposal_id=str(proposal.id),
        )
        return AppliedProposalChange(events=[event], entity_ids={"claim_id": str(claim.id)})

    def _apply_connection(
        self,
        session: Session,
        proposal: Proposal,
        *,
        actor_id: str,
    ) -> AppliedProposalChange:
        payload = proposal.payload
        source_claim_id = self._parse_uuid(
            payload.get("source_claim_id"), field_name="source_claim_id"
        )
        target_claim_id = self._parse_uuid(
            payload.get("target_claim_id"), field_name="target_claim_id"
        )

        self._require_claim(session, source_claim_id)
        self._require_claim(session, target_claim_id)

        connection = CrossFieldConnection(
            source_claim_id=source_claim_id,
            target_claim_id=target_claim_id,
            connection_type=ConnectionType(self._require_str(payload, "connection_type")),
            description=self._require_str(payload, "description"),
            confidence=self._require_float(payload, "confidence"),
            proposal_id=proposal.id,
            status=ProposalStatus.APPROVED,
        )
        session.add(connection)
        session.flush()

        event = PendingEvent(
            event_type="CrossFieldLinkApproved",
            aggregate_type="cross_field_connection",
            aggregate_id=str(connection.id),
            payload={
                "source_claim_id": str(connection.source_claim_id),
                "target_claim_id": str(connection.target_claim_id),
                "connection_type": connection.connection_type.value,
                "description": connection.description,
                "confidence": connection.confidence,
            },
            actor_id=actor_id,
            proposal_id=str(proposal.id),
        )
        return AppliedProposalChange(
            events=[event],
            entity_ids={"connection_id": str(connection.id)},
        )

    def _apply_trust_update(
        self,
        session: Session,
        proposal: Proposal,
        *,
        actor_id: str,
    ) -> AppliedProposalChange:
        payload = proposal.payload
        claim_id = self._parse_uuid(
            proposal.target_entity_id or payload.get("claim_id"),
            field_name="claim_id",
        )
        claim = self._require_claim(session, claim_id)

        target_status = TrustStatus(
            self._require_str(payload, "trust_status", fallback_key="new_status")
        )
        resolved_status = self._trust_engine.resolve(
            TrustTransitionRequest(
                current_status=claim.trust_status,
                target_status=target_status,
                evidence_reliability=self._optional_reliability(
                    payload.get("evidence_reliability")
                ),
                evidence_relationship=self._optional_relationship(
                    payload.get("evidence_relationship")
                ),
                dispute_resolved=bool(payload.get("dispute_resolved", False)),
            )
        )
        previous_status = claim.trust_status
        claim.trust_status = resolved_status
        claim.version += 1
        session.flush()

        event = PendingEvent(
            event_type="ClaimTrustChanged",
            aggregate_type="claim",
            aggregate_id=str(claim.id),
            payload={
                "previous_status": previous_status.value,
                "new_status": claim.trust_status.value,
                "reason": payload.get("reason"),
                "version": claim.version,
            },
            actor_id=actor_id,
            proposal_id=str(proposal.id),
        )
        return AppliedProposalChange(events=[event], entity_ids={"claim_id": str(claim.id)})

    def _apply_add_evidence(
        self,
        session: Session,
        proposal: Proposal,
        *,
        actor_id: str,
    ) -> AppliedProposalChange:
        payload = proposal.payload
        evidence = Evidence(
            evidence_type=EvidenceType(self._require_str(payload, "evidence_type")),
            title=self._require_str(payload, "title"),
            source=self._require_str(payload, "source"),
            excerpt=self._optional_str(payload.get("excerpt")),
            reliability=Reliability(payload.get("reliability", Reliability.UNVERIFIED.value)),
            created_by_id=proposal.proposed_by_id,
        )
        session.add(evidence)
        session.flush()

        claim_links = self._claim_links_from_payload(proposal)
        events = [
            PendingEvent(
                event_type="EvidenceCreated",
                aggregate_type="evidence",
                aggregate_id=str(evidence.id),
                payload={
                    "evidence_type": evidence.evidence_type.value,
                    "title": evidence.title,
                    "source": evidence.source,
                    "reliability": evidence.reliability.value,
                    "excerpt": evidence.excerpt,
                    "claim_links": claim_links,
                },
                actor_id=actor_id,
                proposal_id=str(proposal.id),
            )
        ]

        for item in claim_links:
            claim_id = self._parse_uuid(item.get("claim_id"), field_name="claim_links.claim_id")
            relationship = EvidenceRelationship(
                item.get("relationship", EvidenceRelationship.SUPPORTS.value)
            )
            claim = self._require_claim(session, claim_id)
            session.add(
                ClaimEvidence(
                    claim_id=claim.id,
                    evidence_id=evidence.id,
                    relationship_type=relationship,
                )
            )
            events.append(
                PendingEvent(
                    event_type="EvidenceLinkedToClaim",
                    aggregate_type="evidence",
                    aggregate_id=str(evidence.id),
                    payload={
                        "claim_id": str(claim.id),
                        "relationship": relationship.value,
                    },
                    actor_id=actor_id,
                    proposal_id=str(proposal.id),
                )
            )

            next_status = self._trust_engine.infer_from_evidence(
                claim.trust_status,
                evidence_reliability=evidence.reliability,
                evidence_relationship=relationship,
            )
            if next_status is not claim.trust_status:
                previous_status = claim.trust_status
                claim.trust_status = next_status
                claim.version += 1
                events.append(
                    PendingEvent(
                        event_type="ClaimTrustChanged",
                        aggregate_type="claim",
                        aggregate_id=str(claim.id),
                        payload={
                            "previous_status": previous_status.value,
                            "new_status": next_status.value,
                            "reason": "trust updated from approved evidence",
                            "version": claim.version,
                        },
                        actor_id=actor_id,
                        proposal_id=str(proposal.id),
                    )
                )

        session.flush()
        return AppliedProposalChange(events=events, entity_ids={"evidence_id": str(evidence.id)})

    def _claim_links_from_payload(self, proposal: Proposal) -> list[dict[str, Any]]:
        claim_links = list(proposal.payload.get("claim_links", []))
        if (
            not claim_links
            and proposal.target_entity_type == "claim"
            and proposal.target_entity_id is not None
        ):
            claim_links = [{"claim_id": str(proposal.target_entity_id), "relationship": "supports"}]
        if not claim_links:
            raise ValueError("add_evidence proposals require at least one claim link")
        return claim_links

    @staticmethod
    def _require_claim(session: Session, claim_id: uuid.UUID) -> Claim:
        claim = session.get(Claim, claim_id)
        if claim is None:
            raise LookupError(f"claim '{claim_id}' not found")
        return claim

    @staticmethod
    def _parse_uuid(raw_value: object, *, field_name: str) -> uuid.UUID:
        if isinstance(raw_value, uuid.UUID):
            return raw_value
        if not isinstance(raw_value, str):
            raise ValueError(f"{field_name} must be a UUID string")
        try:
            return uuid.UUID(raw_value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid UUID") from exc

    @staticmethod
    def _require_str(
        payload: dict[str, Any],
        key: str,
        *,
        fallback_key: str | None = None,
    ) -> str:
        value = payload.get(key)
        if value is None and fallback_key is not None:
            value = payload.get(fallback_key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{key} must be a non-empty string")
        return value

    @staticmethod
    def _optional_str(value: object) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("expected a string value")
        return value

    @staticmethod
    def _require_float(payload: dict[str, Any], key: str) -> float:
        value = payload.get(key)
        if not isinstance(value, int | float):
            raise ValueError(f"{key} must be numeric")
        return float(value)

    @staticmethod
    def _optional_reliability(value: object) -> Reliability | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("evidence_reliability must be a string")
        return Reliability(value)

    @staticmethod
    def _optional_relationship(value: object) -> EvidenceRelationship | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("evidence_relationship must be a string")
        return EvidenceRelationship(value)
