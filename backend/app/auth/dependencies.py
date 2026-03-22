from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import TokenPayload, decode_access_token
from app.auth.policy_engine import Operation, PolicyEngine
from app.interfaces import IActorService
from app.schemas import ActorRead, AutonomyLevel


security = HTTPBearer(auto_error=False)


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


async def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> TokenPayload:
    if credentials is None:
        raise _unauthorized("missing bearer token")
    try:
        return decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise _unauthorized("invalid bearer token") from exc


def get_actor_service(request: Request) -> IActorService:
    actor_service = getattr(request.app.state, "actor_service", None)
    if actor_service is None:
        raise RuntimeError("request.app.state.actor_service is not configured")
    return cast(IActorService, actor_service)


async def get_current_actor(
    request: Request,
    token_payload: TokenPayload = Depends(get_current_token_payload),
) -> ActorRead:
    actor_service = get_actor_service(request)
    try:
        return await actor_service.get(token_payload.sub)
    except LookupError as exc:
        raise _unauthorized("actor referenced by token was not found") from exc


def require_permission(
    operation: Operation,
    *,
    autonomy_level: AutonomyLevel = AutonomyLevel.LEVEL_0,
) -> Callable[[ActorRead], Awaitable[ActorRead]]:
    async def dependency(actor: ActorRead = Depends(get_current_actor)) -> ActorRead:
        engine = PolicyEngine(autonomy_level=autonomy_level)
        try:
            engine.assert_allowed(actor, operation)
        except PermissionError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        return actor

    return dependency
