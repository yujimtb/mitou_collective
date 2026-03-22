from __future__ import annotations

import pytest

from app.schemas import EvidenceRelationship, Reliability, TrustStatus
from app.workflows import InvalidTrustTransitionError, TrustTransitionEngine, TrustTransitionRequest


def test_ai_suggested_claim_becomes_tentative_on_approval() -> None:
    engine = TrustTransitionEngine()

    assert engine.approve_claim(TrustStatus.AI_SUGGESTED) is TrustStatus.TENTATIVE


def test_tentative_claim_requires_high_reliability_to_become_established() -> None:
    engine = TrustTransitionEngine()

    assert (
        engine.resolve(
            TrustTransitionRequest(
                current_status=TrustStatus.TENTATIVE,
                target_status=TrustStatus.ESTABLISHED,
                evidence_reliability=Reliability.HIGH,
            )
        )
        is TrustStatus.ESTABLISHED
    )

    with pytest.raises(InvalidTrustTransitionError):
        engine.resolve(
            TrustTransitionRequest(
                current_status=TrustStatus.TENTATIVE,
                target_status=TrustStatus.ESTABLISHED,
                evidence_reliability=Reliability.MEDIUM,
            )
        )


def test_established_claim_requires_contradicting_evidence_to_become_disputed() -> None:
    engine = TrustTransitionEngine()

    assert (
        engine.resolve(
            TrustTransitionRequest(
                current_status=TrustStatus.ESTABLISHED,
                target_status=TrustStatus.DISPUTED,
                evidence_relationship=EvidenceRelationship.CONTRADICTS,
            )
        )
        is TrustStatus.DISPUTED
    )


def test_dispute_resolution_restores_established_status() -> None:
    engine = TrustTransitionEngine()

    assert (
        engine.resolve(
            TrustTransitionRequest(
                current_status=TrustStatus.DISPUTED,
                target_status=TrustStatus.ESTABLISHED,
                dispute_resolved=True,
            )
        )
        is TrustStatus.ESTABLISHED
    )
