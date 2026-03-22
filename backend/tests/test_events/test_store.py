from __future__ import annotations

from collections.abc import Iterator
import uuid

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.events.models import EventRecord, EventStoreBase
from app.events.store import EventStore
from app.models import Actor, Base
from app.schemas import ActorType, TrustLevel


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    EventStoreBase.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    try:
        yield factory
    finally:
        EventStoreBase.metadata.drop_all(engine)
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.mark.asyncio
async def test_append_and_query_events(session_factory: sessionmaker[Session]) -> None:
    store = EventStore(session_factory)

    first = await store.append(
        event_type="ClaimCreated",
        aggregate_type="claim",
        aggregate_id="claim-1",
        payload={"statement": "Initial statement"},
        actor_id="actor-1",
    )
    second = await store.append(
        event_type="ClaimUpdated",
        aggregate_type="claim",
        aggregate_id="claim-1",
        payload={"changes": {"statement": "Updated statement"}, "version": 2},
        actor_id="actor-1",
    )
    third = await store.append(
        event_type="ConceptCreated",
        aggregate_type="concept",
        aggregate_id="concept-1",
        payload={"label": "Entropy"},
        actor_id="actor-2",
    )

    aggregate_events = await store.query_by_aggregate(
        aggregate_type="claim", aggregate_id="claim-1"
    )
    sequence_events = await store.query_by_sequence(after_sequence=1, limit=10)

    assert [first["sequence_number"], second["sequence_number"], third["sequence_number"]] == [
        1,
        2,
        3,
    ]
    assert [event["event_type"] for event in aggregate_events] == ["ClaimCreated", "ClaimUpdated"]
    assert [event["sequence_number"] for event in sequence_events] == [2, 3]


@pytest.mark.asyncio
async def test_append_uses_provided_session_without_committing(session_factory: sessionmaker[Session]) -> None:
    store = EventStore(session_factory)

    with session_factory() as session:
        record = await store.append(
            event_type="ClaimCreated",
            aggregate_type="claim",
            aggregate_id="claim-1",
            payload={"statement": "Initial statement"},
            actor_id="actor-1",
            session=session,
        )
        visible_in_session = session.scalar(
            select(EventRecord).where(EventRecord.sequence_number == record["sequence_number"])
        )

    with session_factory() as session:
        visible_after_close = session.scalar(
            select(EventRecord).where(EventRecord.sequence_number == record["sequence_number"])
        )

    assert visible_in_session is not None
    assert visible_after_close is None


@pytest.mark.asyncio
async def test_limit_must_be_positive(session_factory: sessionmaker[Session]) -> None:
    store = EventStore(session_factory)

    with pytest.raises(ValueError, match="limit"):
        await store.query_by_sequence(limit=0)


@pytest.mark.asyncio
async def test_recent_events_returns_formatted_activity(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        session.add(
                Actor(
                    id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
                    actor_type=ActorType.HUMAN,
                    name="Reviewer One",
                    trust_level=TrustLevel.REVIEWER,
                )
        )
        session.commit()

    store = EventStore(session_factory)
    await store.append(
        event_type="ClaimCreated",
        aggregate_type="claim",
        aggregate_id="claim-1",
        payload={"statement": "Entropy increases"},
        actor_id="11111111-1111-1111-1111-111111111111",
    )
    await store.append(
        event_type="ProposalCreated",
        aggregate_type="proposal",
        aggregate_id="proposal-1",
        payload={"rationale": "Bridge similar claims"},
        actor_id="11111111-1111-1111-1111-111111111111",
    )

    recent = await store.recent_events(limit=2)

    assert [item["kind"] for item in recent] == ["proposal_created", "claim_created"]
    assert recent[0]["actor_name"] == "Reviewer One"
    assert recent[0]["href"] == "/review"
    assert recent[1]["title"] == "Claim作成"
    assert recent[1]["summary"] == "「Entropy increases」を作成"


def test_event_records_cannot_be_updated_or_deleted(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        record = EventRecord(
            event_type="ClaimCreated",
            aggregate_type="claim",
            aggregate_id="claim-1",
            payload={"statement": "Immutable"},
            actor_id="actor-1",
        )
        session.add(record)
        session.commit()
        session.refresh(record)

        record.event_type = "ClaimUpdated"
        with pytest.raises(ValueError, match="append-only"):
            session.commit()
        session.rollback()

        persistent = session.scalar(select(EventRecord).where(EventRecord.sequence_number == 1))
        assert persistent is not None
        session.delete(persistent)
        with pytest.raises(ValueError, match="append-only"):
            session.commit()
