from __future__ import annotations

import asyncio

from app.agent import ContextCollector

from ._fakes import (
    InMemoryClaimService,
    InMemoryConceptService,
    make_claim,
    make_concept,
    make_context,
    make_evidence,
    make_term,
)


def test_collect_for_claim_includes_related_context() -> None:
    claims = [
        make_claim(
            "claim-1",
            statement="Entropy increases in isolated systems.",
            concept_ids=["concept-1"],
            context_ids=["context-1"],
            evidence_ids=["evidence-1"],
        ),
        make_claim(
            "claim-2",
            statement="Black hole area behaves like entropy.",
            concept_ids=["concept-1"],
            context_ids=["context-2"],
        ),
        make_claim(
            "claim-3",
            statement="Free energy bounds useful work.",
            concept_ids=["concept-2"],
            context_ids=["context-1"],
        ),
        make_claim(
            "claim-4",
            statement="Unrelated statement.",
            concept_ids=["concept-3"],
            context_ids=["context-3"],
        ),
    ]
    concepts = [
        make_concept(
            "concept-1",
            label="Entropy",
            description="Entropy as disorder and uncertainty.",
            field="thermodynamics",
        ),
        make_concept(
            "concept-2",
            label="Free energy",
            description="Capacity for work.",
            field="thermodynamics",
        ),
        make_concept(
            "concept-3", label="Graph", description="Network object.", field="mathematics"
        ),
    ]
    contexts = {
        "context-1": make_context(
            "context-1",
            name="Classical Thermodynamics",
            field="thermodynamics",
            assumptions=["closed system"],
        ),
        "context-2": make_context(
            "context-2", name="Black Hole Thermodynamics", field="astrophysics"
        ),
        "context-3": make_context("context-3", name="Graph Theory", field="mathematics"),
    }
    evidence = {"evidence-1": make_evidence("evidence-1", title="Thermodynamics textbook")}

    collector = ContextCollector(
        claim_service=InMemoryClaimService(claims),
        concept_service=InMemoryConceptService(concepts),
        context_loader=lambda context_id: _lookup(contexts, context_id),
        evidence_loader=lambda evidence_id: _lookup(evidence, evidence_id),
    )

    snapshot = asyncio.run(collector.collect_for_claim("claim-1"))

    assert snapshot.source_field == "thermodynamics"
    assert [concept.id for concept in snapshot.concepts] == ["concept-1"]
    assert [context.id for context in snapshot.contexts] == ["context-1"]
    assert [item.id for item in snapshot.evidence] == ["evidence-1"]
    assert {claim.id for claim in snapshot.adjacent_claims} == {"claim-2", "claim-3"}


def test_collect_for_concept_finds_related_claims_and_similar_concepts() -> None:
    claims = [
        make_claim(
            "claim-1", statement="Entropy increases in isolated systems.", concept_ids=["concept-1"]
        ),
        make_claim(
            "claim-2",
            statement="Information entropy measures uncertainty.",
            concept_ids=["concept-2"],
        ),
    ]
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
            description="Information-theoretic entropy.",
            field="information_theory",
            term_ids=["term-2"],
        ),
        make_concept(
            "concept-3",
            label="Pressure",
            description="Mechanical pressure.",
            field="thermodynamics",
        ),
    ]
    terms = {
        "term-1": make_term("term-1", surface_form="entropy", concept_ids=["concept-1"]),
        "term-2": make_term("term-2", surface_form="entropy", concept_ids=["concept-2"]),
    }

    collector = ContextCollector(
        claim_service=InMemoryClaimService(claims),
        concept_service=InMemoryConceptService(concepts),
        term_loader=lambda term_id: _lookup(terms, term_id),
    )

    snapshot = asyncio.run(collector.collect_for_concept("concept-1"))

    assert [term.id for term in snapshot.terms] == ["term-1"]
    assert [claim.id for claim in snapshot.related_claims] == ["claim-1"]
    assert [concept.id for concept in snapshot.similar_concepts] == ["concept-2"]


async def _lookup(items: dict[str, object], item_id: str):
    return items.get(item_id)
