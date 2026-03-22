from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import PaginatedResponse, ProposalRead


class ILinkingAgent(ABC):
    @abstractmethod
    async def suggest_connections(
        self,
        *,
        source_entity_type: str,
        source_entity_id: str,
        target_field: str | None = None,
        actor_id: str,
    ) -> list[ProposalRead]:
        raise NotImplementedError

    @abstractmethod
    async def list_suggestions(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ProposalRead]:
        raise NotImplementedError
