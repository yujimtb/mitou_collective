from __future__ import annotations

from collections.abc import Callable
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.interfaces import IActorService
from app.models import Actor
from app.schemas import ActorCreate, ActorRead, ActorUpdate, PaginatedResponse


SessionFactory = Callable[[], Session]


class ActorService(IActorService):
    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory

    async def create(self, payload: ActorCreate) -> ActorRead:
        actor = Actor(
            actor_type=payload.actor_type,
            name=payload.name,
            trust_level=payload.trust_level,
            agent_model=payload.agent_model,
        )
        with self._session_factory() as session:
            session.add(actor)
            session.commit()
            session.refresh(actor)
            return self._to_schema(actor)

    async def get(self, actor_id: str) -> ActorRead:
        actor_uuid = self._parse_uuid(actor_id)
        with self._session_factory() as session:
            actor = session.get(Actor, actor_uuid)
            if actor is None:
                raise LookupError(f"actor '{actor_id}' not found")
            return self._to_schema(actor)

    async def list(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        **filters: object,
    ) -> PaginatedResponse[ActorRead]:
        if page < 1:
            raise ValueError("page must be at least 1")
        if per_page < 1 or per_page > 100:
            raise ValueError("per_page must be between 1 and 100")

        statement = select(Actor).order_by(Actor.created_at.asc())
        count_statement = select(func.count()).select_from(Actor)

        if actor_type := filters.get("actor_type"):
            statement = statement.where(Actor.actor_type == actor_type)
            count_statement = count_statement.where(Actor.actor_type == actor_type)
        if trust_level := filters.get("trust_level"):
            statement = statement.where(Actor.trust_level == trust_level)
            count_statement = count_statement.where(Actor.trust_level == trust_level)
        if name := filters.get("name"):
            pattern = f"%{name}%"
            statement = statement.where(Actor.name.ilike(pattern))
            count_statement = count_statement.where(Actor.name.ilike(pattern))

        statement = statement.offset((page - 1) * per_page).limit(per_page)

        with self._session_factory() as session:
            total_count = session.scalar(count_statement) or 0
            actors = session.scalars(statement).all()
            return PaginatedResponse[ActorRead](
                total_count=total_count,
                current_page=page,
                per_page=per_page,
                items=[self._to_schema(actor) for actor in actors],
            )

    async def update(self, actor_id: str, payload: ActorUpdate) -> ActorRead:
        actor_uuid = self._parse_uuid(actor_id)
        with self._session_factory() as session:
            actor = session.get(Actor, actor_uuid)
            if actor is None:
                raise LookupError(f"actor '{actor_id}' not found")

            updates = payload.model_dump(exclude_unset=True)
            for field_name, value in updates.items():
                setattr(actor, field_name, value)

            session.add(actor)
            session.commit()
            session.refresh(actor)
            return self._to_schema(actor)

    @staticmethod
    def _parse_uuid(raw_value: str) -> uuid.UUID:
        try:
            return uuid.UUID(raw_value)
        except ValueError as exc:
            raise ValueError("actor_id must be a valid UUID") from exc

    @staticmethod
    def _to_schema(actor: Actor) -> ActorRead:
        return ActorRead(
            id=str(actor.id),
            actor_type=actor.actor_type,
            name=actor.name,
            trust_level=actor.trust_level,
            agent_model=actor.agent_model,
            created_at=actor.created_at,
        )
