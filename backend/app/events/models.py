from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import Index, JSON, DateTime, Integer, String, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EventStoreBase(DeclarativeBase):
    pass


class EventRecord(EventStoreBase):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_aggregate", "aggregate_type", "aggregate_id"),
        Index("ix_events_sequence_number", "sequence_number"),
    )

    sequence_number: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid4())
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    proposal_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "sequence_number": self.sequence_number,
            "event_type": self.event_type,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "payload": dict(self.payload),
            "actor_id": self.actor_id,
            "proposal_id": self.proposal_id,
            "created_at": self.created_at,
        }


@event.listens_for(EventRecord, "before_update", propagate=True)
def prevent_event_updates(*_: object) -> None:
    raise ValueError("Event records are append-only and cannot be updated")


@event.listens_for(EventRecord, "before_delete", propagate=True)
def prevent_event_deletes(*_: object) -> None:
    raise ValueError("Event records are append-only and cannot be deleted")
