from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import EvidenceCreate, EvidenceRead, EvidenceUpdate, PaginatedResponse


class IEvidenceService(ABC):
    @abstractmethod
    async def create(self, payload: EvidenceCreate, actor_id: str) -> EvidenceRead:
        raise NotImplementedError

    @abstractmethod
    async def get(self, evidence_id: str) -> EvidenceRead:
        raise NotImplementedError

    @abstractmethod
    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[EvidenceRead]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, evidence_id: str, payload: EvidenceUpdate, actor_id: str) -> EvidenceRead:
        raise NotImplementedError
