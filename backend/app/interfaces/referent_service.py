from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import PaginatedResponse, ReferentCreate, ReferentRead, ReferentUpdate


class IReferentService(ABC):
    @abstractmethod
    async def create(self, payload: ReferentCreate, actor_id: str) -> ReferentRead:
        raise NotImplementedError

    @abstractmethod
    async def get(self, referent_id: str) -> ReferentRead:
        raise NotImplementedError

    @abstractmethod
    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ReferentRead]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, referent_id: str, payload: ReferentUpdate, actor_id: str) -> ReferentRead:
        raise NotImplementedError
