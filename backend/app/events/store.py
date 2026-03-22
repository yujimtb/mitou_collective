from __future__ import annotations

from collections.abc import Callable
from typing import Any
import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.events.formatting import event_href, event_kind, event_title, summarize_event
from app.events.models import EventRecord
from app.interfaces.event_store import IEventStore
from app.models import Actor


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
        session: Session | None = None,
    ) -> dict[str, object]:
        record = EventRecord(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=dict(payload),
            actor_id=actor_id,
            proposal_id=proposal_id,
        )
        if session is not None:
            session.add(record)
            session.flush()
            return record.to_dict()
        with self._session_factory() as own_session:
            own_session.add(record)
            own_session.commit()
            own_session.refresh(record)
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

    async def recent_events(self, *, limit: int = 10) -> list[dict[str, object]]:
        if limit < 1:
            raise ValueError("limit must be at least 1")

        statement = (
            select(EventRecord)
            .order_by(EventRecord.created_at.desc(), EventRecord.sequence_number.desc())
            .limit(limit)
        )
        with self._session_factory() as session:
            records = session.scalars(statement).all()
            actor_ids = {record.actor_id for record in records}
            actor_names = self._load_actor_names(session, actor_ids)
            return [
                {
                    "id": record.id,
                    "kind": event_kind(record.event_type),
                    "title": event_title(record.event_type),
                    "summary": summarize_event(record.event_type, dict(record.payload)),
                    "actor_name": actor_names.get(record.actor_id, record.actor_id),
                    "timestamp": record.created_at.isoformat(),
                    "href": event_href(
                        record.aggregate_type,
                        record.aggregate_id,
                        proposal_id=record.proposal_id,
                    ),
                }
                for record in records
            ]

    def _fetch(self, statement: Select[tuple[EventRecord]]) -> list[dict[str, object]]:
        with self._session_factory() as session:
            records = session.scalars(statement).all()
            return [record.to_dict() for record in records]

    @staticmethod
    def _load_actor_names(session: Session, actor_ids: set[str]) -> dict[str, str]:
        if not actor_ids:
            return {}
        actor_uuids = []
        for actor_id in actor_ids:
            try:
                actor_uuids.append(uuid.UUID(actor_id))
            except ValueError:
                continue
        if not actor_uuids:
            return {}
        actors = session.scalars(select(Actor).where(Actor.id.in_(actor_uuids))).all()
        return {str(actor.id): actor.name for actor in actors}
