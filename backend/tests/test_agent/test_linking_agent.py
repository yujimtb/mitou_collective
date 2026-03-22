from __future__ import annotations

import asyncio
import json

from app.agent import (
    CandidateGenerator,
    CandidateSearch,
    ContextCollector,
    LinkingAgent,
    LinkingAgentConfig,
    ProposalFormatter,
)

from ._fakes import (
    DEFAULT_AI_ACTOR,
    DEFAULT_HUMAN_ACTOR,
    InMemoryClaimService,
    InMemoryConceptService,
    InMemoryProposalService,
    make_claim,
    make_concept,
    make_context,
)


def test_linking_agent_manual_request_creates_filtered_proposals() -> None:
    claims = [
        make_claim(
            "claim-1",
            statement="Entropy increases in isolated systems.",
            concept_ids=["concept-1"],
            context_ids=["context-1"],
        ),
        make_claim(
            "claim-2",
            statement="Information entropy measures uncertainty.",
            concept_ids=["concept-2"],
            context_ids=["context-2"],
        ),
        make_claim(
            "claim-3",
            statement="Compression tracks information content.",
            concept_ids=["concept-3"],
            context_ids=["context-2"],
        ),
    ]
    concepts = [
        make_concept(
            "concept-1",
            label="Entropy",
            description="Thermodynamic entropy.",
            field="thermodynamics",
        ),
        make_concept(
            "concept-2",
            label="Entropy",
            description="Information entropy.",
            field="information_theory",
        ),
        make_concept(
            "concept-3",
            label="Compression",
            description="Efficient coding.",
            field="information_theory",
        ),
    ]
    contexts = {
        "context-1": make_context(
            "context-1", name="Classical Thermodynamics", field="thermodynamics"
        ),
        "context-2": make_context(
            "context-2", name="Shannon Information Theory", field="information_theory"
        ),
    }

    async def llm_client(prompt: str):
        payload = json.loads(prompt)
        assert payload["source_claim"]["id"] == "claim-1"
        return [
            {
                "target_claim_id": "claim-2",
                "connection_type": "analogous",
                "rationale": "Both claims quantify uncertainty with entropy.",
                "confidence": 0.81,
                "caveats": ["Interpretations differ."],
            },
            {
                "target_claim_id": "claim-3",
                "connection_type": "complements",
                "rationale": "Weak relation.",
                "confidence": 0.18,
                "caveats": [],
            },
        ]

    claim_service = InMemoryClaimService(claims)
    concept_service = InMemoryConceptService(concepts)
    proposal_service = InMemoryProposalService(
        actors={DEFAULT_AI_ACTOR.id: DEFAULT_AI_ACTOR, DEFAULT_HUMAN_ACTOR.id: DEFAULT_HUMAN_ACTOR}
    )
    config = LinkingAgentConfig(suggestion_confidence_threshold=0.3)
    collector = ContextCollector(
        claim_service=claim_service,
        concept_service=concept_service,
        context_loader=lambda context_id: _lookup(contexts, context_id),
    )
    search = CandidateSearch(
        claim_service=claim_service,
        concept_service=concept_service,
        context_loader=lambda context_id: _lookup(contexts, context_id),
        config=config,
    )
    generator = CandidateGenerator(llm_client=llm_client, config=config)
    formatter = ProposalFormatter(proposal_service=proposal_service, config=config)
    agent = LinkingAgent(
        claim_service=claim_service,
        concept_service=concept_service,
        proposal_service=proposal_service,
        collector=collector,
        candidate_search=search,
        candidate_generator=generator,
        proposal_formatter=formatter,
        config=config,
        agent_actor_id=DEFAULT_AI_ACTOR.id,
    )

    created = asyncio.run(
        agent.suggest_connections(
            source_entity_type="claim",
            source_entity_id="claim-1",
            target_field="information_theory",
            actor_id=DEFAULT_HUMAN_ACTOR.id,
        )
    )
    listed = asyncio.run(agent.list_suggestions(min_confidence=0.5))

    assert [proposal.target_entity_id for proposal in created] == ["claim-2"]
    assert created[0].proposed_by.id == DEFAULT_AI_ACTOR.id
    assert created[0].payload["source_claim_id"] == "claim-1"
    assert [proposal.id for proposal in listed.items] == [created[0].id]


async def _lookup(items: dict[str, object], item_id: str):
    return items.get(item_id)
