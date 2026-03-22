from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.auth.policy_engine import Operation, PolicyEngine, ProposalRisk
from app.schemas import ActorRead, ActorType, AutonomyLevel, TrustLevel


def make_actor(*, actor_id: str, actor_type: ActorType, trust_level: TrustLevel) -> ActorRead:
    return ActorRead(
        id=actor_id,
        actor_type=actor_type,
        name=actor_id,
        trust_level=trust_level,
        agent_model="gpt-5.4" if actor_type is ActorType.AI_AGENT else None,
        created_at=datetime.now(UTC),
    )


def test_observer_can_only_read() -> None:
    engine = PolicyEngine()
    actor = make_actor(actor_id="1", actor_type=ActorType.HUMAN, trust_level=TrustLevel.OBSERVER)

    assert engine.is_allowed(actor, Operation.READ) is True
    assert engine.is_allowed(actor, Operation.CREATE_PROPOSAL) is False


def test_admin_can_change_trust_levels() -> None:
    engine = PolicyEngine()
    actor = make_actor(actor_id="1", actor_type=ActorType.HUMAN, trust_level=TrustLevel.ADMIN)

    assert engine.is_allowed(actor, Operation.CHANGE_TRUST_LEVEL) is True
    assert engine.is_allowed(actor, Operation.REBUILD_PROJECTIONS) is True


def test_level_zero_blocks_ai_reviews() -> None:
    engine = PolicyEngine(autonomy_level=AutonomyLevel.LEVEL_0)
    actor = make_actor(actor_id="1", actor_type=ActorType.AI_AGENT, trust_level=TrustLevel.REVIEWER)

    assert engine.can_review_proposal(actor, proposal_author_id="2", risk=ProposalRisk.LOW) is False


def test_level_two_allows_low_risk_ai_review() -> None:
    engine = PolicyEngine(autonomy_level=AutonomyLevel.LEVEL_2)
    actor = make_actor(actor_id="1", actor_type=ActorType.AI_AGENT, trust_level=TrustLevel.REVIEWER)

    assert engine.can_review_proposal(actor, proposal_author_id="2", risk=ProposalRisk.LOW) is True
    assert engine.can_review_proposal(actor, proposal_author_id="2", risk=ProposalRisk.HIGH) is False


def test_self_review_is_rejected() -> None:
    engine = PolicyEngine(autonomy_level=AutonomyLevel.LEVEL_3)
    actor = make_actor(actor_id="1", actor_type=ActorType.HUMAN, trust_level=TrustLevel.REVIEWER)

    with pytest.raises(PermissionError):
        engine.assert_can_review_proposal(actor, proposal_author_id="1")
