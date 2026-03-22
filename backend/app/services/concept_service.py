from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.events.commands import ConceptCreated, ConceptUpdated
from app.interfaces import IConceptService, IEventStore
from app.models import ClaimConcept, Concept, CrossFieldConnection, Referent, Term
from app.schemas import ConceptCreate, ConceptRead, ConceptUpdate, CrossFieldConnectionRead, PaginatedResponse
from app.services._shared import SessionFactory, actor_to_ref, paginate, parse_uuid


class ConceptService(IConceptService):
    def __init__(self, session_factory: SessionFactory, event_store: IEventStore):
        self._session_factory = session_factory
        self._event_store = event_store

    async def create(self, payload: ConceptCreate, actor_id: str) -> ConceptRead:
        with self._session_factory() as session:
            referent_uuid = parse_uuid(payload.referent_id, field_name="referent_id") if payload.referent_id else None
            if referent_uuid is not None and session.get(Referent, referent_uuid) is None:
                raise ValueError(f"Referent ID not found: {payload.referent_id}")
            concept = Concept(
                label=payload.label,
                description=payload.description,
                field=payload.field,
                referent_id=referent_uuid,
                created_by_id=parse_uuid(actor_id, field_name="actor_id"),
            )
            if payload.term_ids:
                parsed_term_ids = [parse_uuid(term_id, field_name="term_id") for term_id in payload.term_ids]
                terms = list(
                    session.scalars(select(Term).where(Term.id.in_(parsed_term_ids))).all()
                )
                if len(terms) != len(payload.term_ids):
                    found = {str(t.id) for t in terms}
                    missing = set(payload.term_ids) - found
                    raise ValueError(f"Term IDs not found: {missing}")
                concept.terms = terms
            session.add(concept)
            session.flush()
            session.refresh(concept)
            schema = self._to_schema(concept)

            await self._event_store.append(
                **ConceptCreated(
                    aggregate_id=schema.id,
                    actor_id=actor_id,
                    label=schema.label,
                    description=schema.description,
                    domain_field=schema.field,
                    term_ids=schema.term_ids,
                    referent_id=schema.referent_id,
                ).to_event(),
                session=session,
            )
            session.commit()

        return schema

    async def get(self, concept_id: str) -> ConceptRead:
        with self._session_factory() as session:
            statement = select(Concept).options(selectinload(Concept.terms), selectinload(Concept.created_by)).where(Concept.id == parse_uuid(concept_id, field_name="concept_id"))
            concept = session.scalar(statement)
            if concept is None:
                raise LookupError(f"concept '{concept_id}' not found")
            return self._to_schema(concept)

    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ConceptRead]:
        statement = select(Concept).options(selectinload(Concept.terms), selectinload(Concept.created_by)).order_by(Concept.created_at.asc())
        if field := filters.get("field"):
            statement = statement.where(Concept.field == field)
        if search := filters.get("search"):
            pattern = f"%{search}%"
            statement = statement.where(or_(Concept.label.ilike(pattern), Concept.description.ilike(pattern)))
        with self._session_factory() as session:
            total_count, records = paginate(session, statement, page=page, per_page=per_page)
            return PaginatedResponse[ConceptRead](
                total_count=total_count,
                current_page=page,
                per_page=per_page,
                items=[self._to_schema(record) for record in records],
            )

    async def update(self, concept_id: str, payload: ConceptUpdate, actor_id: str) -> ConceptRead:
        concept_uuid = parse_uuid(concept_id, field_name="concept_id")
        changes = payload.model_dump(exclude_unset=True)
        with self._session_factory() as session:
            statement = select(Concept).options(selectinload(Concept.terms), selectinload(Concept.created_by)).where(Concept.id == concept_uuid)
            concept = session.scalar(statement)
            if concept is None:
                raise LookupError(f"concept '{concept_id}' not found")
            term_ids = changes.pop("term_ids", None)
            referent_id = changes.pop("referent_id", None) if "referent_id" in changes else None
            for field_name, value in changes.items():
                setattr(concept, field_name, value)
            if term_ids is not None:
                parsed_term_ids = [parse_uuid(term_id, field_name="term_id") for term_id in term_ids]
                terms = list(session.scalars(select(Term).where(Term.id.in_(parsed_term_ids))).all())
                if len(terms) != len(term_ids):
                    found = {str(term.id) for term in terms}
                    missing = set(term_ids) - found
                    raise ValueError(f"Term IDs not found: {missing}")
                concept.terms = terms
                changes["term_ids"] = term_ids
            if "referent_id" in payload.model_fields_set:
                parsed_referent_id = parse_uuid(referent_id, field_name="referent_id") if referent_id else None
                if parsed_referent_id is not None and session.get(Referent, parsed_referent_id) is None:
                    raise ValueError(f"Referent ID not found: {referent_id}")
                concept.referent_id = parsed_referent_id
                changes["referent_id"] = referent_id
            session.add(concept)
            session.flush()
            session.refresh(concept)
            schema = self._to_schema(concept)

            await self._event_store.append(
                **ConceptUpdated(aggregate_id=concept_id, actor_id=actor_id, changes=changes).to_event(),
                session=session,
            )
            session.commit()
        return schema

    async def connections(self, concept_id: str) -> list[CrossFieldConnectionRead]:
        concept_uuid = parse_uuid(concept_id, field_name="concept_id")
        with self._session_factory() as session:
            claim_ids = select(ClaimConcept.claim_id).where(ClaimConcept.concept_id == concept_uuid)
            statement = (
                select(CrossFieldConnection)
                .where(
                    or_(
                        CrossFieldConnection.source_claim_id.in_(claim_ids),
                        CrossFieldConnection.target_claim_id.in_(claim_ids),
                    )
                )
                .order_by(CrossFieldConnection.created_at.asc())
            )
            records = session.scalars(statement).all()
            return [
                CrossFieldConnectionRead(
                    id=str(record.id),
                    source_claim_id=str(record.source_claim_id),
                    target_claim_id=str(record.target_claim_id),
                    connection_type=record.connection_type,
                    description=record.description,
                    confidence=record.confidence,
                    proposal_id=str(record.proposal_id) if record.proposal_id else None,
                    status=record.status,
                    created_at=record.created_at,
                )
                for record in records
            ]

    @staticmethod
    def _to_schema(concept: Concept) -> ConceptRead:
        return ConceptRead(
            id=str(concept.id),
            label=concept.label,
            description=concept.description,
            field=concept.field,
            term_ids=[str(term.id) for term in concept.terms],
            referent_id=str(concept.referent_id) if concept.referent_id else None,
            created_at=concept.created_at,
            created_by=actor_to_ref(concept.created_by),
        )
