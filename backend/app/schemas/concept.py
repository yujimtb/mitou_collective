from __future__ import annotations

from pydantic import Field

from app.schemas.actor import ActorRef
from app.schemas.common import SchemaModel, TimestampedRead


class ConceptCreate(SchemaModel):
    label: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1)
    field: str = Field(min_length=1, max_length=100)
    term_ids: list[str] = Field(default_factory=list)
    referent_id: str | None = None


class ConceptUpdate(SchemaModel):
    label: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    field: str | None = Field(default=None, min_length=1, max_length=100)
    term_ids: list[str] | None = None
    referent_id: str | None = None


class ConceptRead(TimestampedRead):
    label: str
    description: str
    field: str
    term_ids: list[str] = Field(default_factory=list)
    referent_id: str | None = None
    created_by: ActorRef | None = None
