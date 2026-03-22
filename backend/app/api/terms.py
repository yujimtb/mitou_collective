from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_term_service
from app.auth.dependencies import require_permission
from app.auth.policy_engine import Operation
from app.interfaces import ITermService
from app.schemas import ActorRead, PaginatedResponse, TermCreate, TermRead, TermUpdate


router = APIRouter(prefix="/terms", tags=["terms"])


@router.get("", response_model=PaginatedResponse[TermRead])
async def list_terms(
    search: str | None = Query(default=None),
    language: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    _: ActorRead = Depends(require_permission(Operation.READ)),
    term_service: ITermService = Depends(get_term_service),
) -> PaginatedResponse[TermRead]:
    return await term_service.list(search=search, language=language, page=page, per_page=per_page)


@router.post("", response_model=TermRead, status_code=status.HTTP_201_CREATED)
async def create_term(
    payload: TermCreate,
    actor: ActorRead = Depends(require_permission(Operation.WRITE)),
    term_service: ITermService = Depends(get_term_service),
) -> TermRead:
    return await term_service.create(payload, actor.id)


@router.get("/{term_id}", response_model=TermRead)
async def get_term(
    term_id: str,
    _: ActorRead = Depends(require_permission(Operation.READ)),
    term_service: ITermService = Depends(get_term_service),
) -> TermRead:
    return await term_service.get(term_id)


@router.put("/{term_id}", response_model=TermRead)
async def update_term(
    term_id: str,
    payload: TermUpdate,
    actor: ActorRead = Depends(require_permission(Operation.WRITE)),
    term_service: ITermService = Depends(get_term_service),
) -> TermRead:
    return await term_service.update(term_id, payload, actor.id)