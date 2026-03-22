from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import Field

from app.api.dependencies import get_linking_agent
from app.auth.dependencies import require_permission
from app.auth.policy_engine import Operation
from app.interfaces import ILinkingAgent
from app.schemas import ActorRead, ErrorResponse, PaginatedResponse, ProposalRead, ProposalStatus
from app.schemas.common import SchemaModel


class SuggestConnectionsRequest(SchemaModel):
    source_entity_type: str = Field(min_length=1, max_length=50)
    source_entity_id: str = Field(min_length=1)
    target_field: str | None = Field(default=None, max_length=100)


class SuggestConnectionsAccepted(SchemaModel):
    job_id: str
    items: list[ProposalRead] = Field(default_factory=list)


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/suggest-connections", response_model=SuggestConnectionsAccepted, status_code=status.HTTP_202_ACCEPTED)
async def suggest_connections(
    payload: SuggestConnectionsRequest,
    request: Request,
    actor: ActorRead = Depends(require_permission(Operation.CREATE_PROPOSAL)),
    linking_agent: ILinkingAgent = Depends(get_linking_agent),
) -> SuggestConnectionsAccepted | JSONResponse:
    llm_config = getattr(request.app.state, "llm_config", None)
    if not llm_config or not getattr(llm_config, "api_key", ""):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                error={
                    "code": "llm_unavailable",
                    "message": "LLM service is not configured",
                    "details": {},
                }
            ).model_dump(mode="json"),
        )

    items = await linking_agent.suggest_connections(
        source_entity_type=payload.source_entity_type,
        source_entity_id=payload.source_entity_id,
        target_field=payload.target_field,
        actor_id=actor.id,
    )
    return SuggestConnectionsAccepted(job_id=str(uuid.uuid4()), items=items)


@router.get("/suggestions", response_model=PaginatedResponse[ProposalRead])
async def list_suggestions(
    status_filter: ProposalStatus | None = Query(default=None, alias="status"),
    min_confidence: float | None = Query(default=None, ge=0.0, le=1.0),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    _: ActorRead = Depends(require_permission(Operation.READ)),
    linking_agent: ILinkingAgent = Depends(get_linking_agent),
) -> PaginatedResponse[ProposalRead]:
    return await linking_agent.list_suggestions(
        status=status_filter,
        min_confidence=min_confidence,
        page=page,
        per_page=per_page,
    )
