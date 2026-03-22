from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import CIRCreate, CIRRead, CIRUpdate


class ICIRService(ABC):
    @abstractmethod
    async def create(self, payload: CIRCreate, actor_id: str) -> CIRRead:
        raise NotImplementedError

    @abstractmethod
    async def get_by_claim(self, claim_id: str) -> CIRRead | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, claim_id: str, payload: CIRUpdate, actor_id: str) -> CIRRead:
        raise NotImplementedError
