from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import PaginatedResponse, ProposalCreate, ProposalRead, ProposalUpdate


class IProposalService(ABC):
    @abstractmethod
    async def create(self, payload: ProposalCreate, actor_id: str) -> ProposalRead:
        raise NotImplementedError

    @abstractmethod
    async def get(self, proposal_id: str) -> ProposalRead:
        raise NotImplementedError

    @abstractmethod
    async def list(self, *, page: int = 1, per_page: int = 20, **filters: object) -> PaginatedResponse[ProposalRead]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, proposal_id: str, payload: ProposalUpdate, actor_id: str) -> ProposalRead:
        raise NotImplementedError
