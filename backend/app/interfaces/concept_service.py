from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import ConceptCreate, ConceptRead, ConceptUpdate, CrossFieldConnectionRead, PaginatedResponse


class IConceptService(ABC):
    @abstractmethod
    async def create(self, payload: ConceptCreate, actor_id: str) -> ConceptRead:
        raise NotImplementedError

    @abstractmethod
    async def get(self, concept_id: str) -> ConceptRead:
        raise NotImplementedError

    @abstractmethod
    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ConceptRead]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, concept_id: str, payload: ConceptUpdate, actor_id: str) -> ConceptRead:
        raise NotImplementedError

    @abstractmethod
    async def connections(self, concept_id: str) -> list[CrossFieldConnectionRead]:
        raise NotImplementedError
