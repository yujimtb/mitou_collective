from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import ContextCreate, ContextRead, ContextUpdate, PaginatedResponse


class IContextService(ABC):
    @abstractmethod
    async def create(self, payload: ContextCreate, actor_id: str) -> ContextRead:
        raise NotImplementedError

    @abstractmethod
    async def get(self, context_id: str) -> ContextRead:
        raise NotImplementedError

    @abstractmethod
    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ContextRead]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, context_id: str, payload: ContextUpdate, actor_id: str) -> ContextRead:
        raise NotImplementedError
