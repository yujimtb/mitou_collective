from __future__ import annotations

from dataclasses import dataclass

from app.schemas import EvidenceRelationship, Reliability, TrustStatus


class InvalidTrustTransitionError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class TrustTransitionRequest:
    current_status: TrustStatus
    target_status: TrustStatus
    evidence_reliability: Reliability | None = None
    evidence_relationship: EvidenceRelationship | None = None
    dispute_resolved: bool = False


class TrustTransitionEngine:
    def approve_claim(self, status: TrustStatus) -> TrustStatus:
        if status is TrustStatus.AI_SUGGESTED:
            return TrustStatus.TENTATIVE
        return status

    def resolve(self, request: TrustTransitionRequest) -> TrustStatus:
        if request.current_status is request.target_status:
            return request.current_status

        current_status = request.current_status
        target_status = request.target_status

        if current_status is TrustStatus.AI_SUGGESTED and target_status is TrustStatus.TENTATIVE:
            return target_status

        if current_status is TrustStatus.TENTATIVE and target_status is TrustStatus.ESTABLISHED:
            if request.evidence_reliability is Reliability.HIGH:
                return target_status
            raise InvalidTrustTransitionError(
                "tentative claims require high-reliability evidence to become established"
            )

        if current_status is TrustStatus.ESTABLISHED and target_status is TrustStatus.DISPUTED:
            if request.evidence_relationship is EvidenceRelationship.CONTRADICTS:
                return target_status
            raise InvalidTrustTransitionError(
                "established claims require contradicting evidence to become disputed"
            )

        if current_status is TrustStatus.DISPUTED and target_status is TrustStatus.ESTABLISHED:
            if request.dispute_resolved:
                return target_status
            raise InvalidTrustTransitionError(
                "disputed claims require an explicit dispute resolution to become established"
            )

        raise InvalidTrustTransitionError(
            f"unsupported trust transition '{current_status.value}' -> '{target_status.value}'"
        )

    def infer_from_evidence(
        self,
        current_status: TrustStatus,
        *,
        evidence_reliability: Reliability,
        evidence_relationship: EvidenceRelationship,
    ) -> TrustStatus:
        if (
            current_status is TrustStatus.TENTATIVE
            and evidence_reliability is Reliability.HIGH
            and evidence_relationship
            in {EvidenceRelationship.SUPPORTS, EvidenceRelationship.PARTIALLY_SUPPORTS}
        ):
            return TrustStatus.ESTABLISHED

        if (
            current_status is TrustStatus.ESTABLISHED
            and evidence_relationship is EvidenceRelationship.CONTRADICTS
        ):
            return TrustStatus.DISPUTED

        return current_status
