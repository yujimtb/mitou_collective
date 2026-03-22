from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import ReviewCreate, ReviewRead


class IReviewService(ABC):
    @abstractmethod
    async def create(self, payload: ReviewCreate, actor_id: str) -> ReviewRead:
        raise NotImplementedError

    @abstractmethod
    async def list_for_proposal(self, proposal_id: str) -> list[ReviewRead]:
        raise NotImplementedError
