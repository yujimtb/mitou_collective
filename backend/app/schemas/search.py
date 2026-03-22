from __future__ import annotations

from pydantic import Field

from app.schemas.common import SchemaModel


class SearchQuery(SchemaModel):
    q: str = Field(min_length=1)
    scope: str | None = Field(default=None, max_length=50)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class SearchResultItem(SchemaModel):
    entity_type: str
    entity_id: str
    title: str
    snippet: str | None = None
    score: float = Field(ge=0.0)


class SearchResult(SchemaModel):
    total_count: int = Field(ge=0)
    items: list[SearchResultItem] = Field(default_factory=list)
