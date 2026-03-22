from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest

from app.auth.dependencies import get_current_actor, get_current_token_payload, require_permission
from app.auth.jwt import JWTSettings, create_access_token, decode_access_token
from app.auth.policy_engine import Operation
from app.schemas import ActorRead, ActorType, TrustLevel


class StubActorService:
    def __init__(self, actor: ActorRead):
        self.actor = actor

    async def get(self, actor_id: str) -> ActorRead:
        if actor_id != self.actor.id:
            raise LookupError(actor_id)
        return self.actor


def make_actor(*, actor_id: str, trust_level: TrustLevel = TrustLevel.REVIEWER) -> ActorRead:
    return ActorRead(
        id=actor_id,
        actor_type=ActorType.HUMAN,
        name="Tester",
        trust_level=trust_level,
        agent_model=None,
        created_at=datetime.now(UTC),
    )


def build_app(actor: ActorRead, settings: JWTSettings) -> FastAPI:
    app = FastAPI()
    app.state.actor_service = StubActorService(actor)

    @app.get("/whoami")
    async def whoami(current_actor: ActorRead = Depends(get_current_actor)) -> dict[str, str]:
        return {"id": current_actor.id}

    @app.get("/review-only")
    async def review_only(
        current_actor: ActorRead = Depends(require_permission(Operation.REVIEW_PROPOSAL)),
    ) -> dict[str, str]:
        return {"id": current_actor.id}

    app.dependency_overrides[get_current_token_payload] = lambda: make_decoded_payload(actor, settings)
    return app


def make_decoded_payload(actor: ActorRead, settings: JWTSettings):
    token = create_access_token(actor, settings=settings)
    return decode_access_token(token.access_token, settings=settings)


def test_missing_bearer_token_is_unauthorized() -> None:
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_token_payload(None))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "missing bearer token"


def test_get_current_actor_uses_actor_service() -> None:
    actor = make_actor(actor_id="11111111-1111-1111-1111-111111111111")
    settings = JWTSettings(secret_key="test-secret")
    app = build_app(actor, settings)

    client = TestClient(app)
    response = client.get("/whoami")

    assert response.status_code == 200
    assert response.json() == {"id": actor.id}


def test_require_permission_returns_forbidden_for_observer() -> None:
    actor = make_actor(
        actor_id="11111111-1111-1111-1111-111111111111",
        trust_level=TrustLevel.OBSERVER,
    )
    settings = JWTSettings(secret_key="test-secret")
    app = build_app(actor, settings)

    client = TestClient(app)
    response = client.get("/review-only")

    assert response.status_code == 403
    assert "not allowed" in response.json()["detail"]


