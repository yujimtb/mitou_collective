from __future__ import annotations

import asyncio
import uuid

import pytest

from app.errors import ConflictError
from app.events.store import EventStore
from app.models import Actor
from app.models import Claim as ClaimModel
from app.schemas import ClaimCreate, ClaimType, ClaimUpdate, ConceptCreate, ContextCreate, TrustStatus
from app.schemas import ActorType, TrustLevel
from app.services import ClaimService, ConceptService, ContextService


class FailingEventStore(EventStore):
    async def append(self, *args, **kwargs):
        await super().append(*args, **kwargs)
        raise RuntimeError("event write failed")


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


def test_claim_service_list_filters_context_by_uuid_or_name(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)

    uuid_named_context = asyncio.run(
        context_service.create(
            ContextCreate(name="not-a-uuid", description="Fallback by name", field="physics", assumptions=[]),
            actor_id,
        )
    )
    standard_context = asyncio.run(
        context_service.create(
            ContextCreate(name="Thermodynamics", description="Primary", field="physics", assumptions=[]),
            actor_id,
        )
    )

    fallback_claim = asyncio.run(
        claim_service.create(
            ClaimCreate(statement="Fallback claim", claim_type=ClaimType.THEOREM, context_ids=[uuid_named_context.id]),
            actor_id,
        )
    )
    uuid_claim = asyncio.run(
        claim_service.create(
            ClaimCreate(statement="UUID claim", claim_type=ClaimType.THEOREM, context_ids=[standard_context.id]),
            actor_id,
        )
    )

    by_uuid = asyncio.run(claim_service.list(context=standard_context.id))
    by_name = asyncio.run(claim_service.list(context="Thermodynamics"))
    by_invalid_uuid = asyncio.run(claim_service.list(context="not-a-uuid"))

    assert [item.id for item in by_uuid.items] == [uuid_claim.id]
    assert [item.id for item in by_name.items] == [uuid_claim.id]
    assert [item.id for item in by_invalid_uuid.items] == [fallback_claim.id]


def test_claim_service_history_formatted_returns_empty_when_no_events(session_factory, event_store) -> None:
    claim_service = ClaimService(session_factory, event_store)

    history = asyncio.run(claim_service.history_formatted(str(uuid.uuid4())))

    assert history == []


def test_claim_service_history_formatted_resolves_actor_and_summary(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)

    with session_factory() as session:
        session.add(
            Actor(
                id=uuid.UUID(actor_id),
                actor_type=ActorType.HUMAN,
                name="Researcher A",
                trust_level=TrustLevel.REVIEWER,
            )
        )
        session.commit()

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="History Context", description="History", field="physics", assumptions=[]),
            actor_id,
        )
    )
    created = asyncio.run(
        claim_service.create(
            ClaimCreate(statement="Entropy rises", claim_type=ClaimType.THEOREM, context_ids=[context.id]),
            actor_id,
        )
    )
    asyncio.run(
        claim_service.update(
            created.id,
            ClaimUpdate(statement="Entropy never decreases"),
            actor_id,
        )
    )

    history = asyncio.run(claim_service.history_formatted(created.id))

    assert [event["title"] for event in history] == ["Claim作成", "Claim更新"]
    assert history[0]["actor_name"] == "Researcher A"
    assert history[0]["summary"] == "「Entropy rises」を作成"
    assert history[1]["summary"] == "更新項目: statement"
    assert history[0]["event_type"] == "ClaimCreated"


def test_claim_service_retract_marks_claim_and_records_event(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Retraction Context", description="Retraction", field="physics", assumptions=[]),
            actor_id,
        )
    )
    created = asyncio.run(
        claim_service.create(
            ClaimCreate(statement="Retractable claim", claim_type=ClaimType.THEOREM, context_ids=[context.id]),
            actor_id,
        )
    )

    retracted = asyncio.run(claim_service.retract(created.id, actor_id))
    history = asyncio.run(claim_service.history(created.id))

    assert retracted.trust_status is TrustStatus.RETRACTED
    assert history[-1]["event_type"] == "ClaimRetracted"


def test_claim_service_retract_raises_conflict_when_already_retracted(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Conflict Context", description="Conflict", field="physics", assumptions=[]),
            actor_id,
        )
    )
    created = asyncio.run(
        claim_service.create(
            ClaimCreate(statement="Already retracted", claim_type=ClaimType.THEOREM, context_ids=[context.id]),
            actor_id,
        )
    )
    asyncio.run(claim_service.retract(created.id, actor_id))

    with pytest.raises(ConflictError, match="already retracted"):
        asyncio.run(claim_service.retract(created.id, actor_id))


def test_claim_service_retract_raises_not_found_for_missing_claim(session_factory, event_store) -> None:
    claim_service = ClaimService(session_factory, event_store)

    with pytest.raises(LookupError, match="not found"):
        asyncio.run(claim_service.retract(str(uuid.uuid4()), "11111111-1111-1111-1111-111111111111"))


def test_claim_created_event_stores_context_names_not_ids(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Classical Thermodynamics", description="Thermo", field="physics", assumptions=[]),
            actor_id,
        )
    )
    created = asyncio.run(
        claim_service.create(
            ClaimCreate(statement="Test context names", claim_type=ClaimType.THEOREM, context_ids=[context.id]),
            actor_id,
        )
    )

    events = asyncio.run(event_store.query_by_aggregate(aggregate_type="claim", aggregate_id=created.id))
    claim_created = next(e for e in events if e["event_type"] == "ClaimCreated")

    assert claim_created["payload"]["context_names"] == ["Classical Thermodynamics"]
    assert claim_created["payload"]["context_names"] != [context.id]


def test_claim_create_rolls_back_when_event_append_fails(session_factory) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, EventStore(session_factory))
    claim_service = ClaimService(session_factory, FailingEventStore(session_factory))

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Atomicity Context", description="Atomicity", field="physics", assumptions=[]),
            actor_id,
        )
    )

    with pytest.raises(RuntimeError, match="event write failed"):
        asyncio.run(
            claim_service.create(
                ClaimCreate(statement="Should rollback", claim_type=ClaimType.THEOREM, context_ids=[context.id]),
                actor_id,
            )
        )

    with session_factory() as session:
        claims = session.query(ClaimModel).all()

    assert claims == []


def test_claim_create_rejects_missing_related_ids(session_factory, event_store) -> None:
    claim_service = ClaimService(session_factory, event_store)

    with pytest.raises(ValueError, match="Context IDs not found"):
        asyncio.run(
            claim_service.create(
                ClaimCreate(
                    statement="Missing context",
                    claim_type=ClaimType.THEOREM,
                    context_ids=[str(uuid.uuid4())],
                ),
                "11111111-1111-1111-1111-111111111111",
            )
        )
