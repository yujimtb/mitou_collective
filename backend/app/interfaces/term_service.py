from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import PaginatedResponse, TermCreate, TermRead, TermUpdate


class ITermService(ABC):
    @abstractmethod
    async def create(self, payload: TermCreate, actor_id: str) -> TermRead:
        raise NotImplementedError

    @abstractmethod
    async def get(self, term_id: str) -> TermRead:
        raise NotImplementedError

    @abstractmethod
    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[TermRead]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, term_id: str, payload: TermUpdate, actor_id: str) -> TermRead:
        raise NotImplementedError
