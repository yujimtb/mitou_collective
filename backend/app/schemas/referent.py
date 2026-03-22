from __future__ import annotations

from pydantic import Field

from app.schemas.actor import ActorRef
from app.schemas.common import SchemaModel, TimestampedRead


class ReferentCreate(SchemaModel):
    label: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)


class ReferentUpdate(SchemaModel):
    label: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class ReferentRead(TimestampedRead):
    label: str
    description: str
    created_by: ActorRef | None = None
