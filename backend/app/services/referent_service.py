from __future__ import annotations

from sqlalchemy import select

from app.interfaces import IEventStore, IReferentService
from app.models import Referent
from app.schemas import PaginatedResponse, ReferentCreate, ReferentRead, ReferentUpdate
from app.services._shared import SessionFactory, actor_to_ref, paginate, parse_uuid


class ReferentService(IReferentService):
    def __init__(self, session_factory: SessionFactory, event_store: IEventStore):
        self._session_factory = session_factory
        self._event_store = event_store

    async def create(self, payload: ReferentCreate, actor_id: str) -> ReferentRead:
        referent = Referent(
            label=payload.label,
            description=payload.description,
            created_by_id=parse_uuid(actor_id, field_name="actor_id"),
        )
        with self._session_factory() as session:
            session.add(referent)
            session.commit()
            session.refresh(referent)
            schema = self._to_schema(referent)

        await self._event_store.append(
            event_type="ReferentCreated",
            aggregate_type="referent",
            aggregate_id=schema.id,
            payload={"label": schema.label, "description": schema.description},
            actor_id=actor_id,
        )
        return schema

    async def get(self, referent_id: str) -> ReferentRead:
        with self._session_factory() as session:
            referent = session.get(Referent, parse_uuid(referent_id, field_name="referent_id"))
            if referent is None:
                raise LookupError(f"referent '{referent_id}' not found")
            return self._to_schema(referent)

    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ReferentRead]:
        statement = select(Referent).order_by(Referent.created_at.asc())
        if label := filters.get("label"):
            statement = statement.where(Referent.label.ilike(f"%{label}%"))
        with self._session_factory() as session:
            total_count, records = paginate(session, statement, page=page, per_page=per_page)
            return PaginatedResponse[ReferentRead](
                total_count=total_count,
                current_page=page,
                per_page=per_page,
                items=[self._to_schema(record) for record in records],
            )

    async def update(self, referent_id: str, payload: ReferentUpdate, actor_id: str) -> ReferentRead:
        referent_uuid = parse_uuid(referent_id, field_name="referent_id")
        changes = payload.model_dump(exclude_unset=True)
        with self._session_factory() as session:
            referent = session.get(Referent, referent_uuid)
            if referent is None:
                raise LookupError(f"referent '{referent_id}' not found")
            for field_name, value in changes.items():
                setattr(referent, field_name, value)
            session.add(referent)
            session.commit()
            session.refresh(referent)
            schema = self._to_schema(referent)

        await self._event_store.append(
            event_type="ReferentUpdated",
            aggregate_type="referent",
            aggregate_id=referent_id,
            payload={"changes": changes},
            actor_id=actor_id,
        )
        return schema

    @staticmethod
    def _to_schema(referent: Referent) -> ReferentRead:
        return ReferentRead(
            id=str(referent.id),
            label=referent.label,
            description=referent.description,
            created_at=referent.created_at,
            created_by=actor_to_ref(referent.created_by),
        )
