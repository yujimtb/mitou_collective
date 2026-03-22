from __future__ import annotations

from pydantic import Field

from app.schemas.actor import ActorRef
from app.schemas.common import SchemaModel, TimestampedRead


class ContextCreate(SchemaModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    field: str = Field(min_length=1, max_length=100)
    assumptions: list[str] = Field(default_factory=list)
    parent_context_id: str | None = None


class ContextUpdate(SchemaModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    field: str | None = Field(default=None, min_length=1, max_length=100)
    assumptions: list[str] | None = None
    parent_context_id: str | None = None


class ContextRead(TimestampedRead):
    name: str
    description: str
    field: str
    assumptions: list[str] = Field(default_factory=list)
    parent_context_id: str | None = None
    created_by: ActorRef | None = None
