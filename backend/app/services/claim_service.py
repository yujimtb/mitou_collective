from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.events.commands import ClaimCreated, ClaimTrustChanged, ClaimUpdated
from app.interfaces import IClaimService, IEventStore
from app.models import CIR, Claim, ClaimConcept, ClaimContext, ClaimEvidence, Concept, Context, Evidence
from app.schemas import CIRRead, ClaimCreate, ClaimRead, ClaimUpdate, PaginatedResponse
from app.services._shared import SessionFactory, actor_to_ref, paginate, parse_uuid


class ClaimService(IClaimService):
    def __init__(self, session_factory: SessionFactory, event_store: IEventStore):
        self._session_factory = session_factory
        self._event_store = event_store

    async def create(self, payload: ClaimCreate, actor_id: str) -> ClaimRead:
        with self._session_factory() as session:
            claim = Claim(
                statement=payload.statement,
                claim_type=payload.claim_type,
                trust_status=payload.trust_status,
                version=1,
                created_by_id=parse_uuid(actor_id, field_name="actor_id"),
            )
            session.add(claim)
            session.flush()

            if payload.context_ids:
                contexts = session.scalars(select(Context).where(Context.id.in_([parse_uuid(item, field_name="context_id") for item in payload.context_ids]))).all()
                claim.context_links = [ClaimContext(claim_id=claim.id, context_id=context.id) for context in contexts]
            if payload.concept_ids:
                concepts = session.scalars(select(Concept).where(Concept.id.in_([parse_uuid(item, field_name="concept_id") for item in payload.concept_ids]))).all()
                claim.concept_links = [ClaimConcept(claim_id=claim.id, concept_id=concept.id, role="related") for concept in concepts]
            if payload.evidence_ids:
                evidence = session.scalars(select(Evidence).where(Evidence.id.in_([parse_uuid(item, field_name="evidence_id") for item in payload.evidence_ids]))).all()
                claim.evidence_links = [ClaimEvidence(claim_id=claim.id, evidence_id=item.id) for item in evidence]
            if payload.cir_id:
                cir = session.get(CIR, parse_uuid(payload.cir_id, field_name="cir_id"))
                if cir is None:
                    raise LookupError(f"cir '{payload.cir_id}' not found")
                cir.claim_id = claim.id

            session.commit()
            persisted = session.scalar(self._detail_statement().where(Claim.id == claim.id))
            assert persisted is not None
            schema = self._to_schema(persisted)

        await self._event_store.append(
            **ClaimCreated(
                aggregate_id=schema.id,
                actor_id=actor_id,
                statement=schema.statement,
                claim_type=schema.claim_type.value,
                trust_status=schema.trust_status.value,
                version=schema.version,
                context_ids=schema.context_ids,
                context_names=schema.context_ids,
                concept_ids=schema.concept_ids,
                evidence_ids=schema.evidence_ids,
                cir_id=schema.cir.id if schema.cir else None,
            ).to_event()
        )
        return schema

    async def get(self, claim_id: str) -> ClaimRead:
        with self._session_factory() as session:
            claim = session.scalar(self._detail_statement().where(Claim.id == parse_uuid(claim_id, field_name="claim_id")))
            if claim is None:
                raise LookupError(f"claim '{claim_id}' not found")
            return self._to_schema(claim)

    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ClaimRead]:
        statement = self._detail_statement().order_by(Claim.created_at.asc())
        if claim_type := filters.get("claim_type"):
            statement = statement.where(Claim.claim_type == claim_type)
        if trust_status := filters.get("trust_status"):
            statement = statement.where(Claim.trust_status == trust_status)
        if search := filters.get("search"):
            statement = statement.where(Claim.statement.ilike(f"%{search}%"))
        if context_name := filters.get("context"):
            statement = statement.join(Claim.context_links).join(ClaimContext.context).where(Context.name == context_name)
        if field := filters.get("field"):
            statement = statement.join(Claim.context_links).join(ClaimContext.context).where(Context.field == field)
        with self._session_factory() as session:
            total_count, records = paginate(session, statement.distinct(), page=page, per_page=per_page)
            return PaginatedResponse[ClaimRead](
                total_count=total_count,
                current_page=page,
                per_page=per_page,
                items=[self._to_schema(record) for record in records],
            )

    async def update(self, claim_id: str, payload: ClaimUpdate, actor_id: str) -> ClaimRead:
        claim_uuid = parse_uuid(claim_id, field_name="claim_id")
        changes = payload.model_dump(exclude_unset=True)
        trust_change = None
        with self._session_factory() as session:
            claim = session.scalar(self._detail_statement().where(Claim.id == claim_uuid))
            if claim is None:
                raise LookupError(f"claim '{claim_id}' not found")

            previous_status = claim.trust_status
            context_ids = changes.pop("context_ids", None)
            concept_ids = changes.pop("concept_ids", None)
            evidence_ids = changes.pop("evidence_ids", None)
            cir_id = changes.pop("cir_id", None) if "cir_id" in changes else None

            for field_name, value in changes.items():
                setattr(claim, field_name, value)

            if context_ids is not None:
                contexts = session.scalars(select(Context).where(Context.id.in_([parse_uuid(item, field_name="context_id") for item in context_ids]))).all()
                claim.context_links = [ClaimContext(claim_id=claim.id, context_id=context.id) for context in contexts]
                changes["context_ids"] = context_ids
            if concept_ids is not None:
                concepts = session.scalars(select(Concept).where(Concept.id.in_([parse_uuid(item, field_name="concept_id") for item in concept_ids]))).all()
                claim.concept_links = [ClaimConcept(claim_id=claim.id, concept_id=concept.id, role="related") for concept in concepts]
                changes["concept_ids"] = concept_ids
            if evidence_ids is not None:
                evidence = session.scalars(select(Evidence).where(Evidence.id.in_([parse_uuid(item, field_name="evidence_id") for item in evidence_ids]))).all()
                claim.evidence_links = [ClaimEvidence(claim_id=claim.id, evidence_id=item.id) for item in evidence]
                changes["evidence_ids"] = evidence_ids
            if "cir_id" in payload.model_fields_set:
                if cir_id:
                    cir = session.get(CIR, parse_uuid(cir_id, field_name="cir_id"))
                    if cir is None:
                        raise LookupError(f"cir '{cir_id}' not found")
                    cir.claim_id = claim.id
                elif claim.cir is not None:
                    session.delete(claim.cir)
                changes["cir_id"] = cir_id

            claim.version += 1
            if claim.trust_status != previous_status:
                trust_change = (previous_status, claim.trust_status, claim.version)

            session.add(claim)
            session.commit()
            persisted = session.scalar(self._detail_statement().where(Claim.id == claim_uuid))
            assert persisted is not None
            schema = self._to_schema(persisted)

        await self._event_store.append(
            **ClaimUpdated(aggregate_id=claim_id, actor_id=actor_id, changes=changes, version=schema.version).to_event()
        )
        if trust_change is not None:
            previous_status, new_status, version = trust_change
            await self._event_store.append(
                **ClaimTrustChanged(
                    aggregate_id=claim_id,
                    actor_id=actor_id,
                    previous_status=previous_status.value,
                    new_status=new_status.value,
                    version=version,
                ).to_event()
            )
        return schema

    async def history(self, claim_id: str) -> list[dict[str, object]]:
        return await self._event_store.query_by_aggregate(aggregate_type="claim", aggregate_id=claim_id)

    @staticmethod
    def _detail_statement():
        return select(Claim).options(
            selectinload(Claim.context_links).selectinload(ClaimContext.context),
            selectinload(Claim.concept_links).selectinload(ClaimConcept.concept),
            selectinload(Claim.evidence_links).selectinload(ClaimEvidence.evidence),
            selectinload(Claim.cir),
            selectinload(Claim.created_by),
        )

    @staticmethod
    def _to_schema(claim: Claim) -> ClaimRead:
        cir = claim.cir
        cir_schema = None
        if cir is not None:
            cir_schema = CIRRead(
                id=str(cir.id),
                claim_id=str(cir.claim_id),
                context_ref=cir.context_ref,
                subject=cir.subject,
                relation=cir.relation,
                object=cir.object,
                conditions=cir.conditions,
                units=cir.units,
                definition_refs=list(cir.definition_refs),
                created_at=cir.created_at,
            )

        return ClaimRead(
            id=str(claim.id),
            statement=claim.statement,
            claim_type=claim.claim_type,
            trust_status=claim.trust_status,
            context_ids=[str(link.context_id) for link in claim.context_links],
            concept_ids=[str(link.concept_id) for link in claim.concept_links],
            evidence_ids=[str(link.evidence_id) for link in claim.evidence_links],
            cir=cir_schema,
            created_at=claim.created_at,
            created_by=actor_to_ref(claim.created_by),
            version=claim.version,
        )
