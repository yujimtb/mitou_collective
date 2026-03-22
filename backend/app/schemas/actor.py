from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import ActorType, SchemaModel, TimestampedRead, TrustLevel


class ActorRef(SchemaModel):
    id: str
    actor_type: ActorType
    name: str
    trust_level: TrustLevel
    agent_model: str | None = None


class ActorCreate(SchemaModel):
    actor_type: ActorType
    name: str = Field(min_length=1, max_length=255)
    trust_level: TrustLevel = TrustLevel.CONTRIBUTOR
    agent_model: str | None = Field(default=None, max_length=100)


class ActorUpdate(SchemaModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    trust_level: TrustLevel | None = None
    agent_model: str | None = Field(default=None, max_length=100)


class ActorRead(TimestampedRead):
    actor_type: ActorType
    name: str
    trust_level: TrustLevel
    agent_model: str | None = None


class AuthToken(SchemaModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
