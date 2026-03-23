from __future__ import annotations

from app.auth.policy_engine import ProposalRisk
from app.schemas import ProposalStatus, ProposalType, ReviewDecision


class InvalidStateTransitionError(ValueError):
    pass


FINAL_PROPOSAL_STATUSES = frozenset(
    {
        ProposalStatus.APPROVED,
        ProposalStatus.REJECTED,
        ProposalStatus.WITHDRAWN,
    }
)


class ProposalStateMachine:
    _RISK_BY_TYPE = {
        ProposalType.CREATE_CLAIM: ProposalRisk.HIGH,
        ProposalType.LINK_CLAIMS: ProposalRisk.HIGH,
        ProposalType.UPDATE_TRUST: ProposalRisk.HIGH,
        ProposalType.ADD_EVIDENCE: ProposalRisk.LOW,
        ProposalType.CONNECT_CONCEPTS: ProposalRisk.HIGH,
    }

    def classify_risk(self, proposal_type: ProposalType) -> ProposalRisk:
        return self._RISK_BY_TYPE[proposal_type]

    def start_review(self, status: ProposalStatus) -> ProposalStatus:
        if status in FINAL_PROPOSAL_STATUSES:
            raise InvalidStateTransitionError(
                f"cannot start review for proposal in final status '{status.value}'"
            )
        if status is ProposalStatus.PENDING:
            return ProposalStatus.IN_REVIEW
        return status

    def apply_review(self, status: ProposalStatus, decision: ReviewDecision) -> ProposalStatus:
        self.start_review(status)

        if decision is ReviewDecision.APPROVE:
            return ProposalStatus.APPROVED
        if decision is ReviewDecision.REJECT:
            return ProposalStatus.REJECTED
        if decision is ReviewDecision.REQUEST_CHANGES:
            return ProposalStatus.IN_REVIEW

        raise InvalidStateTransitionError(f"unsupported review decision '{decision.value}'")

    def withdraw(self, status: ProposalStatus) -> ProposalStatus:
        if status in {ProposalStatus.PENDING, ProposalStatus.IN_REVIEW}:
            return ProposalStatus.WITHDRAWN
        raise InvalidStateTransitionError(f"cannot withdraw proposal from status '{status.value}'")

    def assert_editable(self, status: ProposalStatus) -> None:
        if status not in {ProposalStatus.PENDING, ProposalStatus.IN_REVIEW}:
            raise InvalidStateTransitionError(f"cannot edit proposal in status '{status.value}'")
