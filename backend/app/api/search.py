from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_search_service
from app.auth.dependencies import require_permission
from app.auth.policy_engine import Operation
from app.interfaces import ISearchService
from app.schemas import ActorRead, SearchQuery, SearchResult


router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResult)
async def search(
    q: str = Query(min_length=1),
    scope: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    _: ActorRead = Depends(require_permission(Operation.READ)),
    search_service: ISearchService = Depends(get_search_service),
) -> SearchResult:
    return await search_service.search(SearchQuery(q=q, scope=scope, page=page, per_page=per_page))