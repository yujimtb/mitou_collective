from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_evidence_service
from app.auth.dependencies import require_permission
from app.auth.policy_engine import Operation
from app.interfaces import IEvidenceService
from app.schemas import ActorRead, EvidenceCreate, EvidenceRead, EvidenceType, EvidenceUpdate, PaginatedResponse, Reliability


router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("", response_model=PaginatedResponse[EvidenceRead])
async def list_evidence(
    evidence_type: EvidenceType | None = Query(default=None),
    reliability: Reliability | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    _: ActorRead = Depends(require_permission(Operation.READ)),
    evidence_service: IEvidenceService = Depends(get_evidence_service),
) -> PaginatedResponse[EvidenceRead]:
    return await evidence_service.list(
        evidence_type=evidence_type,
        reliability=reliability,
        search=search,
        page=page,
        per_page=per_page,
    )


@router.post("", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    payload: EvidenceCreate,
    actor: ActorRead = Depends(require_permission(Operation.WRITE)),
    evidence_service: IEvidenceService = Depends(get_evidence_service),
) -> EvidenceRead:
    return await evidence_service.create(payload, actor.id)


@router.get("/{evidence_id}", response_model=EvidenceRead)
async def get_evidence(
    evidence_id: str,
    _: ActorRead = Depends(require_permission(Operation.READ)),
    evidence_service: IEvidenceService = Depends(get_evidence_service),
) -> EvidenceRead:
    return await evidence_service.get(evidence_id)


@router.put("/{evidence_id}", response_model=EvidenceRead)
async def update_evidence(
    evidence_id: str,
    payload: EvidenceUpdate,
    actor: ActorRead = Depends(require_permission(Operation.WRITE)),
    evidence_service: IEvidenceService = Depends(get_evidence_service),
) -> EvidenceRead:
    return await evidence_service.update(evidence_id, payload, actor.id)