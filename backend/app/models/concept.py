from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedByMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Concept(UUIDPrimaryKeyMixin, TimestampMixin, CreatedByMixin, Base):
    __tablename__ = "concepts"
    __table_args__ = (
        Index("ix_concepts_label", "label"),
        Index("ix_concepts_field", "field"),
    )

    label: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    field: Mapped[str] = mapped_column(String(100), nullable=False)
    referent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("referents.id", ondelete="SET NULL"),
        nullable=True,
    )

    referent = relationship("Referent", back_populates="concepts")
    terms = relationship("Term", secondary="term_concepts", back_populates="concepts")
    claim_links = relationship("ClaimConcept", back_populates="concept")
