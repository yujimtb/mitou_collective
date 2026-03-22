from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_context_service
from app.auth.dependencies import require_permission
from app.auth.policy_engine import Operation
from app.interfaces import IContextService
from app.schemas import ActorRead, ContextCreate, ContextRead, ContextUpdate, PaginatedResponse


router = APIRouter(prefix="/contexts", tags=["contexts"])


@router.get("", response_model=PaginatedResponse[ContextRead])
async def list_contexts(
    field: str | None = Query(default=None),
    name: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    _: ActorRead = Depends(require_permission(Operation.READ)),
    context_service: IContextService = Depends(get_context_service),
) -> PaginatedResponse[ContextRead]:
    return await context_service.list(field=field, name=name, page=page, per_page=per_page)


@router.post("", response_model=ContextRead, status_code=status.HTTP_201_CREATED)
async def create_context(
    payload: ContextCreate,
    actor: ActorRead = Depends(require_permission(Operation.WRITE)),
    context_service: IContextService = Depends(get_context_service),
) -> ContextRead:
    return await context_service.create(payload, actor.id)


@router.get("/{context_id}", response_model=ContextRead)
async def get_context(
    context_id: str,
    _: ActorRead = Depends(require_permission(Operation.READ)),
    context_service: IContextService = Depends(get_context_service),
) -> ContextRead:
    return await context_service.get(context_id)


@router.put("/{context_id}", response_model=ContextRead)
async def update_context(
    context_id: str,
    payload: ContextUpdate,
    actor: ActorRead = Depends(require_permission(Operation.WRITE)),
    context_service: IContextService = Depends(get_context_service),
) -> ContextRead:
    return await context_service.update(context_id, payload, actor.id)