from __future__ import annotations

from enum import StrEnum

from app.schemas import ActorRead, ActorType, AutonomyLevel, TrustLevel


class Operation(StrEnum):
    READ = "read"
    WRITE = "write"
    CREATE_PROPOSAL = "create_proposal"
    REVIEW_PROPOSAL = "review_proposal"
    CHANGE_TRUST_LEVEL = "change_trust_level"
    REBUILD_PROJECTIONS = "rebuild_projections"


class ProposalRisk(StrEnum):
    LOW = "low"
    HIGH = "high"


class PolicyEngine:
    def __init__(self, *, autonomy_level: AutonomyLevel = AutonomyLevel.LEVEL_0):
        self.autonomy_level = autonomy_level

    def is_allowed(self, actor: ActorRead, operation: Operation) -> bool:
        match actor.trust_level:
            case TrustLevel.ADMIN:
                return True
            case TrustLevel.REVIEWER:
                return operation in {
                    Operation.READ,
                    Operation.WRITE,
                    Operation.CREATE_PROPOSAL,
                    Operation.REVIEW_PROPOSAL,
                }
            case TrustLevel.CONTRIBUTOR:
                return operation in {Operation.READ, Operation.CREATE_PROPOSAL}
            case TrustLevel.OBSERVER:
                return operation is Operation.READ
        return False

    def assert_allowed(self, actor: ActorRead, operation: Operation) -> None:
        if not self.is_allowed(actor, operation):
            raise PermissionError(f"actor '{actor.id}' is not allowed to perform '{operation.value}'")

    def can_review_proposal(
        self,
        actor: ActorRead,
        *,
        proposal_author_id: str,
        risk: ProposalRisk = ProposalRisk.HIGH,
    ) -> bool:
        if actor.id == proposal_author_id:
            return False

        if not self.is_allowed(actor, Operation.REVIEW_PROPOSAL):
            return False

        if actor.actor_type is ActorType.HUMAN:
            return True

        return self._ai_review_allowed(actor=actor, risk=risk)

    def assert_can_review_proposal(
        self,
        actor: ActorRead,
        *,
        proposal_author_id: str,
        risk: ProposalRisk = ProposalRisk.HIGH,
    ) -> None:
        if actor.id == proposal_author_id:
            raise PermissionError("proposal authors cannot review their own proposals")
        if not self.can_review_proposal(actor, proposal_author_id=proposal_author_id, risk=risk):
            raise PermissionError("actor is not allowed to review the proposal")

    def _ai_review_allowed(self, *, actor: ActorRead, risk: ProposalRisk) -> bool:
        if self.autonomy_level is AutonomyLevel.LEVEL_0:
            return False
        if self.autonomy_level is AutonomyLevel.LEVEL_1:
            return risk is ProposalRisk.LOW
        if self.autonomy_level is AutonomyLevel.LEVEL_2:
            return risk is ProposalRisk.LOW
        if self.autonomy_level is AutonomyLevel.LEVEL_3:
            return True
        return False
