from __future__ import annotations

from pydantic import Field

from app.schemas.actor import ActorRef
from app.schemas.common import SchemaModel, TimestampedRead


class TermCreate(SchemaModel):
    surface_form: str = Field(min_length=1, max_length=500)
    language: str = Field(default="en", min_length=2, max_length=10)
    field_hint: str | None = Field(default=None, max_length=100)
    concept_ids: list[str] = Field(default_factory=list)


class TermUpdate(SchemaModel):
    surface_form: str | None = Field(default=None, min_length=1, max_length=500)
    language: str | None = Field(default=None, min_length=2, max_length=10)
    field_hint: str | None = Field(default=None, max_length=100)
    concept_ids: list[str] | None = None


class TermRead(TimestampedRead):
    surface_form: str
    language: str
    field_hint: str | None = None
    concept_ids: list[str] = Field(default_factory=list)
    created_by: ActorRef | None = None
