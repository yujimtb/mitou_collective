from __future__ import annotations

from collections.abc import Callable
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Actor
from app.schemas import ActorRef


SessionFactory = Callable[[], Session]


def parse_uuid(raw_value: str, *, field_name: str) -> uuid.UUID:
    try:
        return uuid.UUID(raw_value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid UUID") from exc


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
