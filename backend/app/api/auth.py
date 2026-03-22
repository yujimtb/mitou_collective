from __future__ import annotations

from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_actor_service, get_current_actor
from app.auth.jwt import create_access_token
from app.interfaces import IActorService
from app.schemas import ActorCreate, ActorRead, ActorType, AuthToken, TrustLevel
from app.schemas.common import SchemaModel


class LoginRequest(SchemaModel):
    actor_id: str = Field(min_length=1)


class RegisterRequest(SchemaModel):
    name: str = Field(min_length=1, max_length=200)
    actor_type: ActorType = ActorType.HUMAN
    trust_level: TrustLevel = TrustLevel.CONTRIBUTOR


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthToken)
async def login(
    payload: LoginRequest,
    actor_service: IActorService = Depends(get_actor_service),
) -> AuthToken:
    try:
        actor = await actor_service.get(payload.actor_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="actor not found",
        ) from exc
    return create_access_token(actor)


@router.post("/register", response_model=AuthToken, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    actor_service: IActorService = Depends(get_actor_service),
) -> AuthToken:
    actor = await actor_service.create(
        ActorCreate(
            name=payload.name,
            actor_type=payload.actor_type,
            trust_level=payload.trust_level,
        )
    )
    return create_access_token(actor)


@router.get("/me", response_model=ActorRead)
async def get_me(
    actor: ActorRead = Depends(get_current_actor),
) -> ActorRead:
    return actor
