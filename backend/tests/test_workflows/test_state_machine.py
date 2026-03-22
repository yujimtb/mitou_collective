from __future__ import annotations

import pytest

from app.auth.policy_engine import ProposalRisk
from app.schemas import ProposalStatus, ProposalType, ReviewDecision
from app.workflows import InvalidStateTransitionError, ProposalStateMachine


def test_state_machine_handles_review_decisions() -> None:
    machine = ProposalStateMachine()

    assert machine.start_review(ProposalStatus.PENDING) is ProposalStatus.IN_REVIEW
    assert (
        machine.apply_review(ProposalStatus.PENDING, ReviewDecision.REQUEST_CHANGES)
        is ProposalStatus.IN_REVIEW
    )
    assert (
        machine.apply_review(ProposalStatus.IN_REVIEW, ReviewDecision.APPROVE)
        is ProposalStatus.APPROVED
    )
    assert (
        machine.apply_review(ProposalStatus.IN_REVIEW, ReviewDecision.REJECT)
        is ProposalStatus.REJECTED
    )


def test_state_machine_rejects_final_state_transitions() -> None:
    machine = ProposalStateMachine()

    with pytest.raises(InvalidStateTransitionError):
        machine.start_review(ProposalStatus.APPROVED)

    with pytest.raises(InvalidStateTransitionError):
        machine.withdraw(ProposalStatus.REJECTED)


def test_state_machine_classifies_risk_by_proposal_type() -> None:
    machine = ProposalStateMachine()

    assert machine.classify_risk(ProposalType.ADD_EVIDENCE) is ProposalRisk.LOW
    assert machine.classify_risk(ProposalType.CREATE_CLAIM) is ProposalRisk.HIGH
