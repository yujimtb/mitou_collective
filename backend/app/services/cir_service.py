from __future__ import annotations

from sqlalchemy import select

from app.interfaces import ICIRService, IEventStore
from app.models import CIR
from app.schemas import CIRCreate, CIRRead, CIRUpdate
from app.services._shared import SessionFactory, parse_uuid


class CIRService(ICIRService):
    def __init__(self, session_factory: SessionFactory, event_store: IEventStore):
        self._session_factory = session_factory
        self._event_store = event_store

    async def create(self, payload: CIRCreate, actor_id: str) -> CIRRead:
        with self._session_factory() as session:
            cir = CIR(
                claim_id=parse_uuid(payload.claim_id, field_name="claim_id"),
                context_ref=payload.context_ref,
                subject=payload.subject,
                relation=payload.relation,
                object=payload.object,
                conditions=[condition.model_dump() for condition in payload.conditions],
                units=payload.units,
                definition_refs=list(payload.definition_refs),
            )
            session.add(cir)
            session.commit()
            session.refresh(cir)
            schema = self._to_schema(cir)

        await self._event_store.append(
            event_type="CIRCreated",
            aggregate_type="cir",
            aggregate_id=schema.id,
            payload=schema.model_dump(exclude={"created_at"}),
            actor_id=actor_id,
        )
        return schema

    async def get_by_claim(self, claim_id: str) -> CIRRead | None:
        with self._session_factory() as session:
            cir = session.scalar(select(CIR).where(CIR.claim_id == parse_uuid(claim_id, field_name="claim_id")))
            return None if cir is None else self._to_schema(cir)

    async def update(self, claim_id: str, payload: CIRUpdate, actor_id: str) -> CIRRead:
        claim_uuid = parse_uuid(claim_id, field_name="claim_id")
        changes = payload.model_dump(exclude_unset=True)
        if "conditions" in changes and changes["conditions"] is not None:
            changes["conditions"] = [
                condition if isinstance(condition, dict) else condition.model_dump()
                for condition in changes["conditions"]
            ]
        with self._session_factory() as session:
            cir = session.scalar(select(CIR).where(CIR.claim_id == claim_uuid))
            if cir is None:
                raise LookupError(f"cir for claim '{claim_id}' not found")
            for field_name, value in changes.items():
                setattr(cir, field_name, value)
            session.add(cir)
            session.commit()
            session.refresh(cir)
            schema = self._to_schema(cir)

        await self._event_store.append(
            event_type="CIRUpdated",
            aggregate_type="cir",
            aggregate_id=schema.id,
            payload={"claim_id": claim_id, "changes": changes},
            actor_id=actor_id,
        )
        return schema

    @staticmethod
    def _to_schema(cir: CIR) -> CIRRead:
        return CIRRead(
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
