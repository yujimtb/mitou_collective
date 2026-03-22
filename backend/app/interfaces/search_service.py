from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import SearchQuery, SearchResult


class ISearchService(ABC):
    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResult:
        raise NotImplementedError
