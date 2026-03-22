from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.events.models import EventRecord, EventStoreBase
from app.events.store import EventStore


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    EventStoreBase.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    try:
        yield factory
    finally:
        EventStoreBase.metadata.drop_all(engine)
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
async def test_limit_must_be_positive(session_factory: sessionmaker[Session]) -> None:
    store = EventStore(session_factory)

    with pytest.raises(ValueError, match="limit"):
        await store.query_by_sequence(limit=0)


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
