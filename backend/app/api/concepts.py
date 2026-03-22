from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_concept_service
from app.auth.dependencies import require_permission
from app.auth.policy_engine import Operation
from app.interfaces import IConceptService
from app.schemas import ActorRead, ConceptCreate, ConceptRead, ConceptUpdate, CrossFieldConnectionRead, PaginatedResponse


router = APIRouter(prefix="/concepts", tags=["concepts"])


@router.get("", response_model=PaginatedResponse[ConceptRead])
async def list_concepts(
    field: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    _: ActorRead = Depends(require_permission(Operation.READ)),
    concept_service: IConceptService = Depends(get_concept_service),
) -> PaginatedResponse[ConceptRead]:
    return await concept_service.list(field=field, search=search, page=page, per_page=per_page)


@router.post("", response_model=ConceptRead, status_code=status.HTTP_201_CREATED)
async def create_concept(
    payload: ConceptCreate,
    actor: ActorRead = Depends(require_permission(Operation.WRITE)),
    concept_service: IConceptService = Depends(get_concept_service),
) -> ConceptRead:
    return await concept_service.create(payload, actor.id)


@router.get("/{concept_id}", response_model=ConceptRead)
async def get_concept(
    concept_id: str,
    _: ActorRead = Depends(require_permission(Operation.READ)),
    concept_service: IConceptService = Depends(get_concept_service),
) -> ConceptRead:
    return await concept_service.get(concept_id)


@router.put("/{concept_id}", response_model=ConceptRead)
async def update_concept(
    concept_id: str,
    payload: ConceptUpdate,
    actor: ActorRead = Depends(require_permission(Operation.WRITE)),
    concept_service: IConceptService = Depends(get_concept_service),
) -> ConceptRead:
    return await concept_service.update(concept_id, payload, actor.id)


@router.get("/{concept_id}/connections", response_model=list[CrossFieldConnectionRead])
async def list_concept_connections(
    concept_id: str,
    _: ActorRead = Depends(require_permission(Operation.READ)),
    concept_service: IConceptService = Depends(get_concept_service),
) -> list[CrossFieldConnectionRead]:
    return await concept_service.connections(concept_id)