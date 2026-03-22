from __future__ import annotations

from app.events.commands import CrossFieldLinkProposed
from app.interfaces import IConnectionService, IEventStore
from app.models import CrossFieldConnection
from app.schemas import CrossFieldConnectionCreate, CrossFieldConnectionRead, CrossFieldConnectionUpdate
from app.services._shared import SessionFactory, parse_uuid


class ConnectionService(IConnectionService):
    def __init__(self, session_factory: SessionFactory, event_store: IEventStore):
        self._session_factory = session_factory
        self._event_store = event_store

    async def create(self, payload: CrossFieldConnectionCreate, actor_id: str) -> CrossFieldConnectionRead:
        with self._session_factory() as session:
            connection = CrossFieldConnection(
                source_claim_id=parse_uuid(payload.source_claim_id, field_name="source_claim_id"),
                target_claim_id=parse_uuid(payload.target_claim_id, field_name="target_claim_id"),
                connection_type=payload.connection_type,
                description=payload.description,
                confidence=payload.confidence,
                proposal_id=parse_uuid(payload.proposal_id, field_name="proposal_id") if payload.proposal_id else None,
            )
            session.add(connection)
            session.commit()
            session.refresh(connection)
            schema = self._to_schema(connection)

        await self._event_store.append(
            **CrossFieldLinkProposed(
                aggregate_id=schema.id,
                actor_id=actor_id,
                source_claim_id=schema.source_claim_id,
                target_claim_id=schema.target_claim_id,
                connection_type=schema.connection_type.value,
                description=schema.description,
                confidence=schema.confidence,
                status=schema.status.value,
            ).to_event()
        )
        return schema

    async def get(self, connection_id: str) -> CrossFieldConnectionRead:
        with self._session_factory() as session:
            connection = session.get(CrossFieldConnection, parse_uuid(connection_id, field_name="connection_id"))
            if connection is None:
                raise LookupError(f"connection '{connection_id}' not found")
            return self._to_schema(connection)

    async def update(self, connection_id: str, payload: CrossFieldConnectionUpdate, actor_id: str) -> CrossFieldConnectionRead:
        connection_uuid = parse_uuid(connection_id, field_name="connection_id")
        changes = payload.model_dump(exclude_unset=True)
        with self._session_factory() as session:
            connection = session.get(CrossFieldConnection, connection_uuid)
            if connection is None:
                raise LookupError(f"connection '{connection_id}' not found")
            if "proposal_id" in changes:
                value = changes["proposal_id"]
                connection.proposal_id = parse_uuid(value, field_name="proposal_id") if value else None
            for field_name, value in changes.items():
                if field_name == "proposal_id":
                    continue
                setattr(connection, field_name, value)
            session.add(connection)
            session.commit()
            session.refresh(connection)
            schema = self._to_schema(connection)

        await self._event_store.append(
            event_type="CrossFieldLinkUpdated",
            aggregate_type="cross_field_connection",
            aggregate_id=connection_id,
            payload={"changes": changes},
            actor_id=actor_id,
        )
        return schema

    @staticmethod
    def _to_schema(connection: CrossFieldConnection) -> CrossFieldConnectionRead:
        return CrossFieldConnectionRead(
            id=str(connection.id),
            source_claim_id=str(connection.source_claim_id),
            target_claim_id=str(connection.target_claim_id),
            connection_type=connection.connection_type,
            description=connection.description,
            confidence=connection.confidence,
            proposal_id=str(connection.proposal_id) if connection.proposal_id else None,
            status=connection.status,
            created_at=connection.created_at,
        )
