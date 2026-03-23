from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.events.commands import ContextCreated, ContextUpdated
from app.interfaces import IContextService, IEventStore
from app.models import Context
from app.schemas import ContextCreate, ContextRead, ContextUpdate, PaginatedResponse
from app.services._shared import SessionFactory, actor_to_ref, paginate, parse_uuid, require_related_record


class ContextService(IContextService):
    def __init__(self, session_factory: SessionFactory, event_store: IEventStore):
        self._session_factory = session_factory
        self._event_store = event_store

    async def create(self, payload: ContextCreate, actor_id: str) -> ContextRead:
        with self._session_factory() as session:
            parent_context_id = None
            if payload.parent_context_id:
                parent_context = require_related_record(
                    session,
                    Context,
                    payload.parent_context_id,
                    field_name="parent_context_id",
                    entity_label="Parent context",
                )
                parent_context_id = parent_context.id
            context = Context(
                name=payload.name,
                description=payload.description,
                field=payload.field,
                assumptions=list(payload.assumptions),
                parent_context_id=parent_context_id,
                created_by_id=parse_uuid(actor_id, field_name="actor_id"),
            )
            session.add(context)
            session.flush()
            session.refresh(context)
            schema = self._to_schema(context)

            await self._event_store.append(
                **ContextCreated(
                    aggregate_id=schema.id,
                    actor_id=actor_id,
                    name=schema.name,
                    description=schema.description,
                    domain_field=schema.field,
                    assumptions=schema.assumptions,
                    parent_context_id=schema.parent_context_id,
                ).to_event(),
                session=session,
            )
            session.commit()
        return schema

    async def get(self, context_id: str) -> ContextRead:
        with self._session_factory() as session:
            statement = select(Context).options(selectinload(Context.created_by)).where(Context.id == parse_uuid(context_id, field_name="context_id"))
            context = session.scalar(statement)
            if context is None:
                raise LookupError(f"context '{context_id}' not found")
            return self._to_schema(context)

    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ContextRead]:
        statement = select(Context).options(selectinload(Context.created_by)).order_by(Context.created_at.asc())
        if field := filters.get("field"):
            statement = statement.where(Context.field == field)
        if name := filters.get("name"):
            statement = statement.where(Context.name.ilike(f"%{name}%"))
        with self._session_factory() as session:
            total_count, records = paginate(session, statement, page=page, per_page=per_page)
            return PaginatedResponse[ContextRead](
                total_count=total_count,
                current_page=page,
                per_page=per_page,
                items=[self._to_schema(record) for record in records],
            )

    async def update(self, context_id: str, payload: ContextUpdate, actor_id: str) -> ContextRead:
        context_uuid = parse_uuid(context_id, field_name="context_id")
        changes = payload.model_dump(exclude_unset=True)
        with self._session_factory() as session:
            statement = select(Context).options(selectinload(Context.created_by)).where(Context.id == context_uuid)
            context = session.scalar(statement)
            if context is None:
                raise LookupError(f"context '{context_id}' not found")
            if "parent_context_id" in changes:
                value = changes["parent_context_id"]
                if value:
                    parent_context = require_related_record(
                        session,
                        Context,
                        value,
                        field_name="parent_context_id",
                        entity_label="Parent context",
                    )
                    if parent_context.id == context.id:
                        raise ValueError("parent_context_id must reference a different context")
                    context.parent_context_id = parent_context.id
                else:
                    context.parent_context_id = None
            for field_name, value in changes.items():
                if field_name == "parent_context_id":
                    continue
                setattr(context, field_name, value)
            session.add(context)
            session.flush()
            session.refresh(context)
            schema = self._to_schema(context)

            await self._event_store.append(
                **ContextUpdated(aggregate_id=context_id, actor_id=actor_id, changes=changes).to_event(),
                session=session,
            )
            session.commit()
        return schema

    @staticmethod
    def _to_schema(context: Context) -> ContextRead:
        return ContextRead(
            id=str(context.id),
            name=context.name,
            description=context.description,
            field=context.field,
            assumptions=list(context.assumptions),
            parent_context_id=str(context.parent_context_id) if context.parent_context_id else None,
            created_at=context.created_at,
            created_by=actor_to_ref(context.created_by),
        )
