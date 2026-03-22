from __future__ import annotations

from pydantic import Field

from app.schemas.common import SchemaModel, TimestampedRead


class Condition(SchemaModel):
    predicate: str = Field(min_length=1, max_length=255)
    argument: str = Field(min_length=1, max_length=255)
    negated: bool = False


class CIRCreate(SchemaModel):
    claim_id: str
    context_ref: str = Field(min_length=1, max_length=255)
    subject: str = Field(min_length=1, max_length=500)
    relation: str = Field(min_length=1, max_length=255)
    object: str | None = Field(default=None, max_length=500)
    conditions: list[Condition] = Field(default_factory=list)
    units: str | None = Field(default=None, max_length=100)
    definition_refs: list[str] = Field(default_factory=list)


class CIRUpdate(SchemaModel):
    context_ref: str | None = Field(default=None, min_length=1, max_length=255)
    subject: str | None = Field(default=None, min_length=1, max_length=500)
    relation: str | None = Field(default=None, min_length=1, max_length=255)
    object: str | None = Field(default=None, max_length=500)
    conditions: list[Condition] | None = None
    units: str | None = Field(default=None, max_length=100)
    definition_refs: list[str] | None = None


class CIRRead(TimestampedRead):
    claim_id: str
    context_ref: str
    subject: str
    relation: str
    object: str | None = None
    conditions: list[Condition] = Field(default_factory=list)
    units: str | None = None
    definition_refs: list[str] = Field(default_factory=list)
