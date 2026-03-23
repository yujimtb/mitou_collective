from __future__ import annotations

import asyncio
import uuid

import pytest
from sqlalchemy import select

from app.events.store import EventStore
from app.models import CIR as CIRModel
from app.models import CrossFieldConnection as CrossFieldConnectionModel
from app.models import Evidence as EvidenceModel
from app.models import Referent as ReferentModel
from app.schemas import (
    CIRUpdate,
    CIRCreate,
    ClaimCreate,
    ClaimEvidenceLink,
    ClaimType,
    ConceptCreate,
    ConnectionType,
    ContextCreate,
    ContextUpdate,
    CrossFieldConnectionCreate,
    CrossFieldConnectionUpdate,
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceType,
    Reliability,
    ReferentCreate,
    ReferentUpdate,
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


class FailingEventStore(EventStore):
    async def append(self, *args, **kwargs):
        await super().append(*args, **kwargs)
        raise RuntimeError("event write failed")


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


def test_concept_service_rejects_missing_term_or_referent_ids(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    concept_service = ConceptService(session_factory, event_store)

    with pytest.raises(ValueError, match="Term IDs not found"):
        asyncio.run(
            concept_service.create(
                ConceptCreate(
                    label="Entropy",
                    description="desc",
                    field="physics",
                    term_ids=[str(uuid.uuid4())],
                ),
                actor_id,
            )
        )

    with pytest.raises(ValueError, match="Referent ID not found"):
        asyncio.run(
            concept_service.create(
                ConceptCreate(
                    label="Entropy",
                    description="desc",
                    field="physics",
                    referent_id=str(uuid.uuid4()),
                ),
                actor_id,
            )
        )


def test_term_service_rejects_missing_concept_ids(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    term_service = TermService(session_factory, event_store)

    with pytest.raises(ValueError, match="Concept IDs not found"):
        asyncio.run(
            term_service.create(
                TermCreate(
                    surface_form="entropy",
                    language="en",
                    concept_ids=[str(uuid.uuid4())],
                ),
                actor_id,
            )
        )


def test_context_service_rejects_missing_or_self_parent_context_ids(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)

    with pytest.raises(ValueError, match="Parent context ID not found"):
        asyncio.run(
            context_service.create(
                ContextCreate(
                    name="Child",
                    description="desc",
                    field="physics",
                    assumptions=[],
                    parent_context_id=str(uuid.uuid4()),
                ),
                actor_id,
            )
        )

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Parent", description="desc", field="physics", assumptions=[]),
            actor_id,
        )
    )

    with pytest.raises(ValueError, match="must reference a different context"):
        asyncio.run(
            context_service.update(
                context.id,
                ContextUpdate(parent_context_id=context.id),
                actor_id,
            )
        )


def test_evidence_cir_and_connection_services_reject_missing_related_ids(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)
    evidence_service = EvidenceService(session_factory, event_store)
    cir_service = CIRService(session_factory, event_store)
    connection_service = ConnectionService(session_factory, event_store)

    with pytest.raises(ValueError, match="Claim IDs not found"):
        asyncio.run(
            evidence_service.create(
                EvidenceCreate(
                    evidence_type=EvidenceType.PAPER,
                    title="Paper",
                    source="doi:test",
                    reliability=Reliability.HIGH,
                    claim_links=[ClaimEvidenceLink(claim_id=str(uuid.uuid4()))],
                ),
                actor_id,
            )
        )

    with pytest.raises(ValueError, match="Claim ID not found"):
        asyncio.run(
            cir_service.create(
                CIRCreate(
                    claim_id=str(uuid.uuid4()),
                    context_ref="Thermo",
                    subject="entropy(system)",
                    relation="non_decreasing_over_time",
                ),
                actor_id,
            )
        )

    with pytest.raises(ValueError, match="Source claim ID not found"):
        asyncio.run(
            connection_service.create(
                CrossFieldConnectionCreate(
                    source_claim_id=str(uuid.uuid4()),
                    target_claim_id=str(uuid.uuid4()),
                    connection_type=ConnectionType.ANALOGOUS,
                    description="similar",
                    confidence=0.7,
                ),
                actor_id,
            )
        )

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Validation", description="desc", field="physics", assumptions=[]),
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

    with pytest.raises(ValueError, match="Proposal ID not found"):
        asyncio.run(
            connection_service.create(
                CrossFieldConnectionCreate(
                    source_claim_id=first_claim.id,
                    target_claim_id=second_claim.id,
                    connection_type=ConnectionType.ANALOGOUS,
                    description="similar",
                    confidence=0.7,
                    proposal_id=str(uuid.uuid4()),
                ),
                actor_id,
            )
        )


def test_referent_service_create_and_update_roll_back_when_event_append_fails(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    failing_service = ReferentService(session_factory, FailingEventStore(session_factory))

    with pytest.raises(RuntimeError, match="event write failed"):
        asyncio.run(
            failing_service.create(ReferentCreate(label="quantity", description="desc"), actor_id)
        )

    with session_factory() as session:
        assert session.scalars(select(ReferentModel)).all() == []

    referent_service = ReferentService(session_factory, event_store)
    referent = asyncio.run(
        referent_service.create(ReferentCreate(label="quantity", description="desc"), actor_id)
    )

    with pytest.raises(RuntimeError, match="event write failed"):
        asyncio.run(
            failing_service.update(
                referent.id,
                ReferentUpdate(label="updated quantity"),
                actor_id,
            )
        )

    persisted = asyncio.run(referent_service.get(referent.id))
    assert persisted.label == "quantity"


def test_evidence_service_create_and_update_roll_back_when_event_append_fails(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)
    evidence_service = EvidenceService(session_factory, event_store)
    failing_service = EvidenceService(session_factory, FailingEventStore(session_factory))

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Atomicity Evidence", description="desc", field="physics", assumptions=[]),
            actor_id,
        )
    )
    claim = asyncio.run(
        claim_service.create(
            ClaimCreate(statement="Evidence claim", claim_type=ClaimType.EMPIRICAL, context_ids=[context.id]),
            actor_id,
        )
    )

    payload = EvidenceCreate(
        evidence_type=EvidenceType.PAPER,
        title="Paper",
        source="doi:test",
        reliability=Reliability.HIGH,
        claim_links=[ClaimEvidenceLink(claim_id=claim.id)],
    )

    with pytest.raises(RuntimeError, match="event write failed"):
        asyncio.run(failing_service.create(payload, actor_id))

    with session_factory() as session:
        assert session.scalars(select(EvidenceModel)).all() == []

    evidence = asyncio.run(evidence_service.create(payload, actor_id))

    with pytest.raises(RuntimeError, match="event write failed"):
        asyncio.run(
            failing_service.update(
                evidence.id,
                EvidenceUpdate(title="Updated paper"),
                actor_id,
            )
        )

    persisted = asyncio.run(evidence_service.get(evidence.id))
    assert persisted.title == "Paper"


def test_cir_service_create_and_update_roll_back_when_event_append_fails(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)
    cir_service = CIRService(session_factory, event_store)
    failing_service = CIRService(session_factory, FailingEventStore(session_factory))

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Atomicity CIR", description="desc", field="physics", assumptions=[]),
            actor_id,
        )
    )
    claim = asyncio.run(
        claim_service.create(
            ClaimCreate(statement="CIR claim", claim_type=ClaimType.DEFINITION, context_ids=[context.id]),
            actor_id,
        )
    )

    payload = CIRCreate(
        claim_id=claim.id,
        context_ref="Thermo",
        subject="entropy(system)",
        relation="non_decreasing_over_time",
    )

    with pytest.raises(RuntimeError, match="event write failed"):
        asyncio.run(failing_service.create(payload, actor_id))

    with session_factory() as session:
        assert session.scalars(select(CIRModel)).all() == []

    cir = asyncio.run(cir_service.create(payload, actor_id))

    with pytest.raises(RuntimeError, match="event write failed"):
        asyncio.run(
            failing_service.update(
                claim.id,
                CIRUpdate(context_ref="Updated"),
                actor_id,
            )
        )

    persisted = asyncio.run(cir_service.get_by_claim(claim.id))
    assert persisted is not None
    assert persisted.context_ref == "Thermo"
    assert cir.id == persisted.id


def test_connection_service_create_and_update_roll_back_when_event_append_fails(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)
    connection_service = ConnectionService(session_factory, event_store)
    failing_service = ConnectionService(session_factory, FailingEventStore(session_factory))

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Atomicity Connection", description="desc", field="physics", assumptions=[]),
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

    payload = CrossFieldConnectionCreate(
        source_claim_id=first_claim.id,
        target_claim_id=second_claim.id,
        connection_type=ConnectionType.ANALOGOUS,
        description="similar",
        confidence=0.7,
    )

    with pytest.raises(RuntimeError, match="event write failed"):
        asyncio.run(failing_service.create(payload, actor_id))

    with session_factory() as session:
        assert session.scalars(select(CrossFieldConnectionModel)).all() == []

    connection = asyncio.run(connection_service.create(payload, actor_id))

    with pytest.raises(RuntimeError, match="event write failed"):
        asyncio.run(
            failing_service.update(
                connection.id,
                CrossFieldConnectionUpdate(description="updated"),
                actor_id,
            )
        )

    persisted = asyncio.run(connection_service.get(connection.id))
    assert persisted.description == "similar"
