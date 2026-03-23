from __future__ import annotations

from pydantic import Field
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_proposal_service, get_review_service
from app.auth.dependencies import get_current_actor, require_permission
from app.auth.policy_engine import Operation
from app.interfaces import IProposalService, IReviewService
from app.schemas import (
    ActorRead,
    PaginatedResponse,
    ProposalCreate,
    ProposalRead,
    ProposalStatus,
    ProposalType,
    ProposalUpdate,
    ReviewCreate,
    ReviewRead,
)
class ProposalDetailRead(ProposalRead):
    reviews: list[ReviewRead] = Field(default_factory=list)


router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.get("", response_model=PaginatedResponse[ProposalRead])
async def list_proposals(
    status_filter: ProposalStatus | None = Query(default=None, alias="status"),
    proposed_by: str | None = Query(default=None),
    proposal_type: ProposalType | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    _: ActorRead = Depends(require_permission(Operation.READ)),
    proposal_service: IProposalService = Depends(get_proposal_service),
) -> PaginatedResponse[ProposalRead]:
    return await proposal_service.list(
        status=status_filter,
        proposed_by_id=proposed_by,
        proposal_type=proposal_type,
        page=page,
        per_page=per_page,
    )


@router.post("", response_model=ProposalRead, status_code=status.HTTP_201_CREATED)
async def create_proposal(
    payload: ProposalCreate,
    actor: ActorRead = Depends(require_permission(Operation.CREATE_PROPOSAL)),
    proposal_service: IProposalService = Depends(get_proposal_service),
) -> ProposalRead:
    return await proposal_service.create(payload, actor.id)


@router.get("/{proposal_id}", response_model=ProposalDetailRead)
async def get_proposal(
    proposal_id: str,
    _: ActorRead = Depends(require_permission(Operation.READ)),
    proposal_service: IProposalService = Depends(get_proposal_service),
    review_service: IReviewService = Depends(get_review_service),
) -> ProposalDetailRead:
    proposal = await proposal_service.get(proposal_id)
    reviews = await review_service.list_for_proposal(proposal_id)
    return ProposalDetailRead(**proposal.model_dump(), reviews=reviews)


@router.put("/{proposal_id}", response_model=ProposalRead)
async def update_proposal(
    proposal_id: str,
    payload: ProposalUpdate,
    actor: ActorRead = Depends(get_current_actor),
    proposal_service: IProposalService = Depends(get_proposal_service),
) -> ProposalRead:
    return await proposal_service.update(proposal_id, payload, actor.id)


@router.post("/{proposal_id}/review", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    proposal_id: str,
    payload: ReviewCreate,
    actor: ActorRead = Depends(require_permission(Operation.REVIEW_PROPOSAL)),
    review_service: IReviewService = Depends(get_review_service),
) -> ReviewRead:
    payload_with_proposal = payload.model_copy(update={"proposal_id": proposal_id})
    return await review_service.create(payload_with_proposal, actor.id)
