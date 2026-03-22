from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import os

from jose import JWTError, jwt

from app.schemas import ActorRead, ActorType, AuthToken, TrustLevel
from app.schemas.common import SchemaModel


@dataclass(frozen=True, slots=True)
class JWTSettings:
    secret_key: str = os.getenv("JWT_SECRET_KEY", "development-secret-key")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    expiry_minutes: int = int(os.getenv("JWT_EXPIRY_MINUTES", "60"))
    issuer: str = os.getenv("JWT_ISSUER", "collective-science")
    audience: str = os.getenv("JWT_AUDIENCE", "collective-science-api")


class TokenPayload(SchemaModel):
    sub: str
    actor_type: ActorType
    trust_level: TrustLevel
    exp: int
    iat: int
    iss: str
    aud: str


def create_access_token(
    actor: ActorRead,
    *,
    expires_delta: timedelta | None = None,
    settings: JWTSettings | None = None,
) -> AuthToken:
    jwt_settings = settings or JWTSettings()
    issued_at = datetime.now(UTC)
    expires_at = issued_at + (expires_delta or timedelta(minutes=jwt_settings.expiry_minutes))
    payload = {
        "sub": actor.id,
        "actor_type": actor.actor_type.value,
        "trust_level": actor.trust_level.value,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
        "iss": jwt_settings.issuer,
        "aud": jwt_settings.audience,
    }
    token = jwt.encode(payload, jwt_settings.secret_key, algorithm=jwt_settings.algorithm)
    return AuthToken(access_token=token, expires_at=expires_at)


def decode_access_token(token: str, *, settings: JWTSettings | None = None) -> TokenPayload:
    jwt_settings = settings or JWTSettings()
    try:
        payload = jwt.decode(
            token,
            jwt_settings.secret_key,
            algorithms=[jwt_settings.algorithm],
            audience=jwt_settings.audience,
            issuer=jwt_settings.issuer,
        )
    except JWTError as exc:
        raise ValueError("invalid access token") from exc
    return TokenPayload.model_validate(payload)
