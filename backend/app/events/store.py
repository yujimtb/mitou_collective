from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.events.models import EventRecord
from app.interfaces.event_store import IEventStore


SessionFactory = Callable[[], Session]


class EventStore(IEventStore):
    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory

    async def append(
        self,
        *,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, object],
        actor_id: str,
        proposal_id: str | None = None,
    ) -> dict[str, object]:
        record = EventRecord(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=dict(payload),
            actor_id=actor_id,
            proposal_id=proposal_id,
        )
        with self._session_factory() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record.to_dict()

    async def query_by_aggregate(
        self, *, aggregate_type: str, aggregate_id: str
    ) -> list[dict[str, object]]:
        statement = (
            select(EventRecord)
            .where(EventRecord.aggregate_type == aggregate_type)
            .where(EventRecord.aggregate_id == aggregate_id)
            .order_by(EventRecord.sequence_number.asc())
        )
        return self._fetch(statement)

    async def query_by_sequence(
        self, *, after_sequence: int = 0, limit: int = 1000
    ) -> list[dict[str, object]]:
        if limit < 1:
            raise ValueError("limit must be at least 1")

        statement = (
            select(EventRecord)
            .where(EventRecord.sequence_number > after_sequence)
            .order_by(EventRecord.sequence_number.asc())
            .limit(limit)
        )
        return self._fetch(statement)

    def _fetch(self, statement: Select[tuple[EventRecord]]) -> list[dict[str, object]]:
        with self._session_factory() as session:
            records = session.scalars(statement).all()
            return [record.to_dict() for record in records]
