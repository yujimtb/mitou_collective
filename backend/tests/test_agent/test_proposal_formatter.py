from __future__ import annotations

import asyncio

from app.agent import GeneratedConnectionCandidate, LinkingAgentConfig, ProposalFormatter
from app.schemas import ConnectionType

from ._fakes import DEFAULT_AI_ACTOR, InMemoryProposalService, make_claim_candidate, make_proposal


def test_proposal_formatter_filters_threshold_and_duplicates() -> None:
    existing = [
        make_proposal(
            "proposal-existing",
            actor=DEFAULT_AI_ACTOR,
            payload=make_claim_candidate(
                source_claim_id="claim-1", target_claim_id="claim-2", confidence=0.9
            ),
        )
    ]
    service = InMemoryProposalService(
        actors={DEFAULT_AI_ACTOR.id: DEFAULT_AI_ACTOR}, existing=existing
    )
    formatter = ProposalFormatter(
        proposal_service=service,
        config=LinkingAgentConfig(suggestion_confidence_threshold=0.5),
    )
    candidates = [
        GeneratedConnectionCandidate(
            source_entity_type="claim",
            source_entity_id="claim-1",
            target_entity_type="claim",
            target_entity_id="claim-2",
            connection_type=ConnectionType.ANALOGOUS,
            rationale="Duplicate candidate.",
            confidence=0.9,
            caveats=[],
        ),
        GeneratedConnectionCandidate(
            source_entity_type="claim",
            source_entity_id="claim-1",
            target_entity_type="claim",
            target_entity_id="claim-3",
            connection_type=ConnectionType.GENERALIZES,
            rationale="Unique strong candidate.",
            confidence=0.85,
            caveats=["Assumptions differ."],
        ),
        GeneratedConnectionCandidate(
            source_entity_type="claim",
            source_entity_id="claim-1",
            target_entity_type="claim",
            target_entity_id="claim-4",
            connection_type=ConnectionType.COMPLEMENTS,
            rationale="Below threshold candidate.",
            confidence=0.2,
            caveats=[],
        ),
    ]

    created = asyncio.run(formatter.create_proposals(candidates, actor_id=DEFAULT_AI_ACTOR.id))

    assert [proposal.target_entity_id for proposal in created] == ["claim-3"]
    assert created[0].payload["confidence"] == 0.85
