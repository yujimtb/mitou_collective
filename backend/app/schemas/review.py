from __future__ import annotations

from pydantic import Field

from app.schemas.actor import ActorRef
from app.schemas.common import ReviewDecision, SchemaModel, TimestampedRead


class ReviewCreate(SchemaModel):
    proposal_id: str
    decision: ReviewDecision
    comment: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class ReviewRead(TimestampedRead):
    proposal_id: str
    reviewer: ActorRef
    decision: ReviewDecision
    comment: str | None = None
    confidence: float | None = None
