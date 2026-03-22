from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import ActorCreate, ActorRead, ActorUpdate, PaginatedResponse


class IActorService(ABC):
    @abstractmethod
    async def create(self, payload: ActorCreate) -> ActorRead:
        raise NotImplementedError

    @abstractmethod
    async def get(self, actor_id: str) -> ActorRead:
        raise NotImplementedError

    @abstractmethod
    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ActorRead]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, actor_id: str, payload: ActorUpdate) -> ActorRead:
        raise NotImplementedError
