from __future__ import annotations

import asyncio

from app.schemas import ClaimCreate, ClaimType, ClaimUpdate, ConceptCreate, ContextCreate, TrustStatus
from app.services import ClaimService, ConceptService, ContextService


def test_claim_service_create_update_and_history(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    concept_service = ConceptService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Thermodynamics", description="Thermo context", field="physics", assumptions=[]),
            actor_id,
        )
    )
    concept = asyncio.run(
        concept_service.create(
            ConceptCreate(label="Entropy", description="Meaning", field="physics", term_ids=[]),
            actor_id,
        )
    )

    created = asyncio.run(
        claim_service.create(
            ClaimCreate(
                statement="Entropy increases",
                claim_type=ClaimType.THEOREM,
                context_ids=[context.id],
                concept_ids=[concept.id],
            ),
            actor_id,
        )
    )
    updated = asyncio.run(
        claim_service.update(
            created.id,
            ClaimUpdate(statement="Entropy does not decrease", trust_status=TrustStatus.ESTABLISHED),
            actor_id,
        )
    )
    history = asyncio.run(claim_service.history(created.id))

    assert created.version == 1
    assert updated.version == 2
    assert updated.trust_status is TrustStatus.ESTABLISHED
    assert [event["event_type"] for event in history] == ["ClaimCreated", "ClaimUpdated", "ClaimTrustChanged"]
