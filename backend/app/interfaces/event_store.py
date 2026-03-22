from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class IEventStore(ABC):
    @abstractmethod
    async def append(
        self,
        *,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, object],
        actor_id: str,
        proposal_id: str | None = None,
        session: Session | None = None,
    ) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    async def query_by_aggregate(self, *, aggregate_type: str, aggregate_id: str) -> list[dict[str, object]]:
        raise NotImplementedError

    @abstractmethod
    async def query_by_sequence(self, *, after_sequence: int = 0, limit: int = 1000) -> list[dict[str, object]]:
        raise NotImplementedError

    @abstractmethod
    async def recent_events(self, *, limit: int = 10) -> list[dict[str, object]]:
        raise NotImplementedError
