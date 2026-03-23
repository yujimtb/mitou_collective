from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.events.commands import EvidenceCreated, EvidenceLinkedToClaim
from app.interfaces import IEvidenceService, IEventStore
from app.models import Claim, ClaimEvidence, Evidence
from app.schemas import EvidenceCreate, EvidenceRead, EvidenceUpdate, PaginatedResponse
from app.services._shared import SessionFactory, actor_to_ref, load_required_records, paginate, parse_uuid


class EvidenceService(IEvidenceService):
    def __init__(self, session_factory: SessionFactory, event_store: IEventStore):
        self._session_factory = session_factory
        self._event_store = event_store

    async def create(self, payload: EvidenceCreate, actor_id: str) -> EvidenceRead:
        with self._session_factory() as session:
            claims_by_id: dict[str, Claim] = {}
            if payload.claim_links:
                claim_ids = [link.claim_id for link in payload.claim_links]
                claims_by_id = {
                    claim_id: claim
                    for claim_id, claim in zip(
                        claim_ids,
                        load_required_records(
                            session,
                            Claim,
                            claim_ids,
                            field_name="claim_id",
                            entity_label="Claim",
                        ),
                        strict=True,
                    )
                }

            evidence = Evidence(
                evidence_type=payload.evidence_type,
                title=payload.title,
                source=payload.source,
                excerpt=payload.excerpt,
                reliability=payload.reliability,
                created_by_id=parse_uuid(actor_id, field_name="actor_id"),
            )
            session.add(evidence)
            session.flush()
            for link in payload.claim_links:
                claim = claims_by_id[link.claim_id]
                session.add(
                    ClaimEvidence(
                        claim_id=claim.id,
                        evidence_id=evidence.id,
                        relationship_type=link.relationship,
                    )
                )
            session.flush()
            persisted = session.scalar(self._detail_statement().where(Evidence.id == evidence.id))
            assert persisted is not None
            schema = self._to_schema(persisted)

            await self._event_store.append(
                **EvidenceCreated(
                    aggregate_id=schema.id,
                    actor_id=actor_id,
                    evidence_type=schema.evidence_type.value,
                    title=schema.title,
                    source=schema.source,
                    reliability=schema.reliability.value,
                    excerpt=schema.excerpt,
                    claim_links=[link.model_dump() for link in schema.claim_links],
                ).to_event(),
                session=session,
            )
            for link in schema.claim_links:
                await self._event_store.append(
                    **EvidenceLinkedToClaim(
                        aggregate_id=schema.id,
                        actor_id=actor_id,
                        claim_id=link.claim_id,
                        relationship=link.relationship.value,
                    ).to_event(),
                    session=session,
                )
            session.commit()
        return schema

    async def get(self, evidence_id: str) -> EvidenceRead:
        with self._session_factory() as session:
            evidence = session.scalar(self._detail_statement().where(Evidence.id == parse_uuid(evidence_id, field_name="evidence_id")))
            if evidence is None:
                raise LookupError(f"evidence '{evidence_id}' not found")
            return self._to_schema(evidence)

    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[EvidenceRead]:
        statement = self._detail_statement().order_by(Evidence.created_at.asc())
        if evidence_type := filters.get("evidence_type"):
            statement = statement.where(Evidence.evidence_type == evidence_type)
        if reliability := filters.get("reliability"):
            statement = statement.where(Evidence.reliability == reliability)
        if search := filters.get("search"):
            pattern = f"%{search}%"
            statement = statement.where(or_(Evidence.title.ilike(pattern), Evidence.source.ilike(pattern), Evidence.excerpt.ilike(pattern)))
        with self._session_factory() as session:
            total_count, records = paginate(session, statement, page=page, per_page=per_page)
            return PaginatedResponse[EvidenceRead](
                total_count=total_count,
                current_page=page,
                per_page=per_page,
                items=[self._to_schema(record) for record in records],
            )

    async def update(self, evidence_id: str, payload: EvidenceUpdate, actor_id: str) -> EvidenceRead:
        evidence_uuid = parse_uuid(evidence_id, field_name="evidence_id")
        changes = payload.model_dump(exclude_unset=True)
        with self._session_factory() as session:
            evidence = session.scalar(self._detail_statement().where(Evidence.id == evidence_uuid))
            if evidence is None:
                raise LookupError(f"evidence '{evidence_id}' not found")
            claim_links = changes.pop("claim_links", None)
            for field_name, value in changes.items():
                setattr(evidence, field_name, value)
            if claim_links is not None:
                claim_ids = [link["claim_id"] for link in claim_links]
                claims_by_id = {
                    claim_id: claim
                    for claim_id, claim in zip(
                        claim_ids,
                        load_required_records(
                            session,
                            Claim,
                            claim_ids,
                            field_name="claim_id",
                            entity_label="Claim",
                        ),
                        strict=True,
                    )
                }
                evidence.claim_links = [
                    ClaimEvidence(
                        claim_id=claims_by_id[link["claim_id"]].id,
                        evidence_id=evidence_uuid,
                        relationship_type=link["relationship"],
                    )
                    for link in claim_links
                ]
                changes["claim_links"] = claim_links
            session.add(evidence)
            session.flush()
            persisted = session.scalar(self._detail_statement().where(Evidence.id == evidence_uuid))
            assert persisted is not None
            schema = self._to_schema(persisted)

            await self._event_store.append(
                event_type="EvidenceUpdated",
                aggregate_type="evidence",
                aggregate_id=evidence_id,
                payload={"changes": changes},
                actor_id=actor_id,
                session=session,
            )
            session.commit()
        return schema

    @staticmethod
    def _detail_statement():
        return select(Evidence).options(selectinload(Evidence.claim_links), selectinload(Evidence.created_by))

    @staticmethod
    def _to_schema(evidence: Evidence) -> EvidenceRead:
        return EvidenceRead(
            id=str(evidence.id),
            evidence_type=evidence.evidence_type,
            title=evidence.title,
            source=evidence.source,
            excerpt=evidence.excerpt,
            reliability=evidence.reliability,
            claim_links=[
                {"claim_id": str(link.claim_id), "relationship": link.relationship_type}
                for link in evidence.claim_links
            ],
            created_at=evidence.created_at,
            created_by=actor_to_ref(evidence.created_by),
        )
