from __future__ import annotations

import asyncio

from app.agent import (
    CandidateSearch,
    ClaimContextSnapshot,
    ConceptContextSnapshot,
    LinkingAgentConfig,
)

from ._fakes import (
    InMemoryClaimService,
    InMemoryConceptService,
    make_claim,
    make_concept,
    make_context,
    make_term,
)


def test_search_claim_candidates_prefers_other_fields_and_target_field() -> None:
    source_claim = make_claim(
        "claim-1",
        statement="Entropy increases in isolated systems.",
        concept_ids=["concept-1"],
        context_ids=["context-1"],
    )
    claims = [
        source_claim,
        make_claim(
            "claim-2",
            statement="Information entropy measures uncertainty.",
            concept_ids=["concept-2"],
            context_ids=["context-2"],
        ),
        make_claim(
            "claim-3",
            statement="Entropy production appears in black holes.",
            concept_ids=["concept-3"],
            context_ids=["context-3"],
        ),
        make_claim(
            "claim-4",
            statement="Pressure balances force.",
            concept_ids=["concept-4"],
            context_ids=["context-4"],
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
            description="Information-theoretic entropy.",
            field="information_theory",
        ),
        make_concept(
            "concept-3", label="Entropy", description="Black hole entropy.", field="astrophysics"
        ),
        make_concept(
            "concept-4",
            label="Pressure",
            description="Mechanical pressure.",
            field="thermodynamics",
        ),
    ]
    contexts = {
        "context-1": make_context(
            "context-1", name="Classical Thermodynamics", field="thermodynamics"
        ),
        "context-2": make_context(
            "context-2", name="Information Theory", field="information_theory"
        ),
        "context-3": make_context(
            "context-3", name="Black Hole Thermodynamics", field="astrophysics"
        ),
        "context-4": make_context("context-4", name="Mechanics", field="thermodynamics"),
    }
    snapshot = ClaimContextSnapshot(
        claim=source_claim,
        concepts=[concepts[0]],
        contexts=[contexts["context-1"]],
        evidence=[],
        adjacent_claims=[],
        source_field="thermodynamics",
    )

    search = CandidateSearch(
        claim_service=InMemoryClaimService(claims),
        concept_service=InMemoryConceptService(concepts),
        context_loader=lambda context_id: _lookup(contexts, context_id),
        config=LinkingAgentConfig(max_candidates=5, search_pool_size=10),
    )

    candidates = asyncio.run(
        search.search_claim_candidates(snapshot, target_field="information_theory")
    )

    assert [candidate.entity_id for candidate in candidates] == ["claim-2"]


def test_search_concept_candidates_uses_term_similarity() -> None:
    concepts = [
        make_concept(
            "concept-1",
            label="Entropy",
            description="Thermodynamic entropy.",
            field="thermodynamics",
            term_ids=["term-1"],
        ),
        make_concept(
            "concept-2",
            label="Entropy",
            description="Information entropy.",
            field="information_theory",
            term_ids=["term-2"],
        ),
        make_concept(
            "concept-3",
            label="Momentum",
            description="Linear momentum.",
            field="mechanics",
            term_ids=["term-3"],
        ),
    ]
    terms = {
        "term-1": make_term("term-1", surface_form="entropy"),
        "term-2": make_term("term-2", surface_form="entropy"),
        "term-3": make_term("term-3", surface_form="momentum"),
    }
    snapshot = ConceptContextSnapshot(
        concept=concepts[0],
        terms=[terms["term-1"]],
        related_claims=[],
        similar_concepts=[],
    )

    search = CandidateSearch(
        claim_service=InMemoryClaimService([]),
        concept_service=InMemoryConceptService(concepts),
        term_loader=lambda term_id: _lookup(terms, term_id),
    )

    candidates = asyncio.run(search.search_concept_candidates(snapshot))

    assert [candidate.entity_id for candidate in candidates] == ["concept-2"]


async def _lookup(items: dict[str, object], item_id: str):
    return items.get(item_id)
