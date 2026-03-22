from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.interfaces import IEventStore, ITermService
from app.models import Concept, Term
from app.schemas import PaginatedResponse, TermCreate, TermRead, TermUpdate
from app.services._shared import SessionFactory, actor_to_ref, paginate, parse_uuid


class TermService(ITermService):
    def __init__(self, session_factory: SessionFactory, event_store: IEventStore):
        self._session_factory = session_factory
        self._event_store = event_store

    async def create(self, payload: TermCreate, actor_id: str) -> TermRead:
        with self._session_factory() as session:
            term = Term(
                surface_form=payload.surface_form,
                language=payload.language,
                field_hint=payload.field_hint,
                created_by_id=parse_uuid(actor_id, field_name="actor_id"),
            )
            if payload.concept_ids:
                parsed_concept_ids = [parse_uuid(concept_id, field_name="concept_id") for concept_id in payload.concept_ids]
                concepts = session.scalars(select(Concept).where(Concept.id.in_(parsed_concept_ids))).all()
                if len(concepts) != len(payload.concept_ids):
                    found = {str(concept.id) for concept in concepts}
                    missing = set(payload.concept_ids) - found
                    raise ValueError(f"Concept IDs not found: {missing}")
                term.concepts = list(concepts)
            session.add(term)
            session.flush()
            session.refresh(term)
            schema = self._to_schema(term)

            await self._event_store.append(
                event_type="TermCreated",
                aggregate_type="term",
                aggregate_id=schema.id,
                payload=schema.model_dump(exclude={"created_at", "created_by"}),
                actor_id=actor_id,
                session=session,
            )
            session.commit()
        return schema

    async def get(self, term_id: str) -> TermRead:
        with self._session_factory() as session:
            statement = select(Term).options(selectinload(Term.concepts), selectinload(Term.created_by)).where(Term.id == parse_uuid(term_id, field_name="term_id"))
            term = session.scalar(statement)
            if term is None:
                raise LookupError(f"term '{term_id}' not found")
            return self._to_schema(term)

    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[TermRead]:
        statement = select(Term).options(selectinload(Term.concepts), selectinload(Term.created_by)).order_by(Term.created_at.asc())
        if search := filters.get("search"):
            statement = statement.where(Term.surface_form.ilike(f"%{search}%"))
        if language := filters.get("language"):
            statement = statement.where(Term.language == language)
        with self._session_factory() as session:
            total_count, records = paginate(session, statement, page=page, per_page=per_page)
            return PaginatedResponse[TermRead](
                total_count=total_count,
                current_page=page,
                per_page=per_page,
                items=[self._to_schema(record) for record in records],
            )

    async def update(self, term_id: str, payload: TermUpdate, actor_id: str) -> TermRead:
        term_uuid = parse_uuid(term_id, field_name="term_id")
        changes = payload.model_dump(exclude_unset=True)
        with self._session_factory() as session:
            statement = select(Term).options(selectinload(Term.concepts), selectinload(Term.created_by)).where(Term.id == term_uuid)
            term = session.scalar(statement)
            if term is None:
                raise LookupError(f"term '{term_id}' not found")
            concept_ids = changes.pop("concept_ids", None)
            for field_name, value in changes.items():
                setattr(term, field_name, value)
            if concept_ids is not None:
                parsed_concept_ids = [parse_uuid(concept_id, field_name="concept_id") for concept_id in concept_ids]
                concepts = session.scalars(select(Concept).where(Concept.id.in_(parsed_concept_ids))).all()
                if len(concepts) != len(concept_ids):
                    found = {str(concept.id) for concept in concepts}
                    missing = set(concept_ids) - found
                    raise ValueError(f"Concept IDs not found: {missing}")
                term.concepts = list(concepts)
                changes["concept_ids"] = concept_ids
            session.add(term)
            session.flush()
            session.refresh(term)
            schema = self._to_schema(term)

            await self._event_store.append(
                event_type="TermUpdated",
                aggregate_type="term",
                aggregate_id=term_id,
                payload={"changes": changes},
                actor_id=actor_id,
                session=session,
            )
            session.commit()
        return schema

    @staticmethod
    def _to_schema(term: Term) -> TermRead:
        return TermRead(
            id=str(term.id),
            surface_form=term.surface_form,
            language=term.language,
            field_hint=term.field_hint,
            concept_ids=[str(concept.id) for concept in term.concepts],
            created_at=term.created_at,
            created_by=actor_to_ref(term.created_by),
        )
