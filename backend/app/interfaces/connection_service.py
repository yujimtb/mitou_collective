from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import CrossFieldConnectionCreate, CrossFieldConnectionRead, CrossFieldConnectionUpdate


class IConnectionService(ABC):
    @abstractmethod
    async def create(self, payload: CrossFieldConnectionCreate, actor_id: str) -> CrossFieldConnectionRead:
        raise NotImplementedError

    @abstractmethod
    async def get(self, connection_id: str) -> CrossFieldConnectionRead:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        connection_id: str,
        payload: CrossFieldConnectionUpdate,
        actor_id: str,
    ) -> CrossFieldConnectionRead:
        raise NotImplementedError
