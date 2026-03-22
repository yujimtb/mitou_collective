from __future__ import annotations

import uuid

from sqlalchemy import Enum, Float, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.schemas.common import ReviewDecision


class Review(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reviews"

    proposal_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("actors.id", ondelete="RESTRICT"), nullable=False)
    decision: Mapped[ReviewDecision] = mapped_column(Enum(ReviewDecision, name="review_decision_enum", native_enum=False), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    proposal = relationship("Proposal", back_populates="reviews")
    reviewer = relationship("Actor", lazy="joined")
