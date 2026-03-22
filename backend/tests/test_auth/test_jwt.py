from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.auth.jwt import JWTSettings, create_access_token, decode_access_token
from app.schemas import ActorRead, ActorType, TrustLevel


def make_actor() -> ActorRead:
    return ActorRead(
        id="11111111-1111-1111-1111-111111111111",
        actor_type=ActorType.HUMAN,
        name="Reviewer",
        trust_level=TrustLevel.REVIEWER,
        agent_model=None,
        created_at=datetime.now(UTC),
    )


def test_create_and_decode_access_token() -> None:
    settings = JWTSettings(secret_key="test-secret", expiry_minutes=15)
    token = create_access_token(make_actor(), settings=settings)

    payload = decode_access_token(token.access_token, settings=settings)

    assert payload.sub == "11111111-1111-1111-1111-111111111111"
    assert payload.actor_type is ActorType.HUMAN
    assert payload.trust_level is TrustLevel.REVIEWER


def test_invalid_token_raises_value_error() -> None:
    settings = JWTSettings(secret_key="test-secret")

    with pytest.raises(ValueError):
        decode_access_token("not-a-token", settings=settings)


def test_expired_token_is_rejected() -> None:
    settings = JWTSettings(secret_key="test-secret")
    token = create_access_token(make_actor(), expires_delta=timedelta(seconds=-1), settings=settings)

    with pytest.raises(ValueError):
        decode_access_token(token.access_token, settings=settings)
