from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from typing import TypeVar
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Actor
from app.schemas import ActorRef


SessionFactory = Callable[[], Session]
ModelT = TypeVar("ModelT")


def parse_uuid(raw_value: str, *, field_name: str) -> uuid.UUID:
    try:
        return uuid.UUID(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid UUID") from exc


def load_required_records(
    session: Session,
    model: type[ModelT],
    raw_ids: Sequence[str],
    *,
    field_name: str,
    entity_label: str,
) -> list[ModelT]:
    if not raw_ids:
        return []

    duplicates = sorted(record_id for record_id, count in Counter(raw_ids).items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate {entity_label} IDs provided: {duplicates}")

    parsed_ids = [parse_uuid(record_id, field_name=field_name) for record_id in raw_ids]
    id_column = getattr(model, "id")
    records = list(session.scalars(select(model).where(id_column.in_(parsed_ids))).all())
    records_by_id = {str(record.id): record for record in records}
    missing = sorted(record_id for record_id in raw_ids if record_id not in records_by_id)
    if missing:
        raise ValueError(f"{entity_label} IDs not found: {missing}")

    return [records_by_id[record_id] for record_id in raw_ids]


def require_related_record(
    session: Session,
    model: type[ModelT],
    raw_id: str,
    *,
    field_name: str,
    entity_label: str,
) -> ModelT:
    record = session.get(model, parse_uuid(raw_id, field_name=field_name))
    if record is None:
        raise ValueError(f"{entity_label} ID not found: {raw_id}")
    return record


def actor_to_ref(actor: Actor | None) -> ActorRef | None:
    if actor is None:
        return None
    return ActorRef(
        id=str(actor.id),
        actor_type=actor.actor_type,
        name=actor.name,
        trust_level=actor.trust_level,
        agent_model=actor.agent_model,
    )


def paginate(session: Session, statement, *, page: int, per_page: int):
    if page < 1:
        raise ValueError("page must be at least 1")
    if per_page < 1 or per_page > 100:
        raise ValueError("per_page must be between 1 and 100")

    total_count = session.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    records = session.scalars(statement.offset((page - 1) * per_page).limit(per_page)).all()
    return total_count, records
