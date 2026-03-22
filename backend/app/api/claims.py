from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_claim_service
from app.auth.dependencies import require_permission
from app.auth.policy_engine import Operation
from app.interfaces import IClaimService
from app.schemas import ActorRead, ClaimCreate, ClaimRead, ClaimType, PaginatedResponse, TrustStatus, ClaimUpdate


router = APIRouter(prefix="/claims", tags=["claims"])


@router.get("", response_model=PaginatedResponse[ClaimRead])
async def list_claims(
    context: str | None = Query(default=None),
    field: str | None = Query(default=None),
    trust_status: TrustStatus | None = Query(default=None),
    claim_type: ClaimType | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    _: ActorRead = Depends(require_permission(Operation.READ)),
    claim_service: IClaimService = Depends(get_claim_service),
) -> PaginatedResponse[ClaimRead]:
    return await claim_service.list(
        context=context,
        field=field,
        trust_status=trust_status,
        claim_type=claim_type,
        search=search,
        page=page,
        per_page=per_page,
    )


@router.post("", response_model=ClaimRead, status_code=status.HTTP_201_CREATED)
async def create_claim(
    payload: ClaimCreate,
    actor: ActorRead = Depends(require_permission(Operation.WRITE)),
    claim_service: IClaimService = Depends(get_claim_service),
) -> ClaimRead:
    return await claim_service.create(payload, actor.id)


@router.get("/{claim_id}", response_model=ClaimRead)
async def get_claim(
    claim_id: str,
    _: ActorRead = Depends(require_permission(Operation.READ)),
    claim_service: IClaimService = Depends(get_claim_service),
) -> ClaimRead:
    return await claim_service.get(claim_id)


@router.put("/{claim_id}", response_model=ClaimRead)
async def update_claim(
    claim_id: str,
    payload: ClaimUpdate,
    actor: ActorRead = Depends(require_permission(Operation.WRITE)),
    claim_service: IClaimService = Depends(get_claim_service),
) -> ClaimRead:
    return await claim_service.update(claim_id, payload, actor.id)


@router.get("/{claim_id}/history")
async def get_claim_history(
    claim_id: str,
    _: ActorRead = Depends(require_permission(Operation.READ)),
    claim_service: IClaimService = Depends(get_claim_service),
) -> list[dict[str, object]]:
    return await claim_service.history(claim_id)