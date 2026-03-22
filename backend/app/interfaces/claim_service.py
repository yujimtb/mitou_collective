from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import ClaimCreate, ClaimRead, ClaimUpdate, PaginatedResponse


class IClaimService(ABC):
    @abstractmethod
    async def create(self, payload: ClaimCreate, actor_id: str) -> ClaimRead:
        raise NotImplementedError

    @abstractmethod
    async def get(self, claim_id: str) -> ClaimRead:
        raise NotImplementedError

    @abstractmethod
    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ClaimRead]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, claim_id: str, payload: ClaimUpdate, actor_id: str) -> ClaimRead:
        raise NotImplementedError

    @abstractmethod
    async def history(self, claim_id: str) -> list[dict[str, object]]:
        raise NotImplementedError

    @abstractmethod
    async def history_formatted(self, claim_id: str) -> list[dict[str, object]]:
        raise NotImplementedError

    @abstractmethod
    async def retract(self, claim_id: str, actor_id: str) -> ClaimRead:
        raise NotImplementedError
