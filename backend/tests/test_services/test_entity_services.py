from __future__ import annotations

import asyncio

from app.schemas import (
    CIRCreate,
    ClaimCreate,
    ClaimEvidenceLink,
    ClaimType,
    ConceptCreate,
    ConnectionType,
    ContextCreate,
    CrossFieldConnectionCreate,
    EvidenceCreate,
    EvidenceType,
    Reliability,
    ReferentCreate,
    TermCreate,
)
from app.services import (
    CIRService,
    ClaimService,
    ConceptService,
    ConnectionService,
    ContextService,
    EvidenceService,
    ReferentService,
    TermService,
)


def test_referent_term_concept_and_context_services(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    referent_service = ReferentService(session_factory, event_store)
    term_service = TermService(session_factory, event_store)
    concept_service = ConceptService(session_factory, event_store)
    context_service = ContextService(session_factory, event_store)

    referent = asyncio.run(referent_service.create(ReferentCreate(label="quantity", description="desc"), actor_id))
    term = asyncio.run(term_service.create(TermCreate(surface_form="entropy", language="en"), actor_id))
    concept = asyncio.run(
        concept_service.create(
            ConceptCreate(label="Entropy", description="desc", field="physics", term_ids=[term.id], referent_id=referent.id),
            actor_id,
        )
    )
    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Thermodynamics", description="desc", field="physics", assumptions=["macro"]),
            actor_id,
        )
    )

    assert concept.term_ids == [term.id]
    assert concept.referent_id == referent.id
    assert context.assumptions == ["macro"]


def test_evidence_cir_and_connection_services(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)
    evidence_service = EvidenceService(session_factory, event_store)
    cir_service = CIRService(session_factory, event_store)
    connection_service = ConnectionService(session_factory, event_store)

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Thermo", description="desc", field="physics", assumptions=[]),
            actor_id,
        )
    )
    first_claim = asyncio.run(
        claim_service.create(
            ClaimCreate(statement="Claim A", claim_type=ClaimType.DEFINITION, context_ids=[context.id]),
            actor_id,
        )
    )
    second_claim = asyncio.run(
        claim_service.create(
            ClaimCreate(statement="Claim B", claim_type=ClaimType.THEOREM, context_ids=[context.id]),
            actor_id,
        )
    )

    evidence = asyncio.run(
        evidence_service.create(
            EvidenceCreate(
                evidence_type=EvidenceType.PAPER,
                title="Paper",
                source="doi:test",
                reliability=Reliability.HIGH,
                claim_links=[ClaimEvidenceLink(claim_id=first_claim.id)],
            ),
            actor_id,
        )
    )
    cir = asyncio.run(
        cir_service.create(
            CIRCreate(
                claim_id=first_claim.id,
                context_ref="Thermo",
                subject="entropy(system)",
                relation="non_decreasing_over_time",
            ),
            actor_id,
        )
    )
    connection = asyncio.run(
        connection_service.create(
            CrossFieldConnectionCreate(
                source_claim_id=first_claim.id,
                target_claim_id=second_claim.id,
                connection_type=ConnectionType.ANALOGOUS,
                description="similar",
                confidence=0.7,
            ),
            actor_id,
        )
    )

    assert evidence.claim_links[0].claim_id == first_claim.id
    assert cir.claim_id == first_claim.id
    assert connection.source_claim_id == first_claim.id
