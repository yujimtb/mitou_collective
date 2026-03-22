from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedByMixin, TimestampMixin, UUIDPrimaryKeyMixin


class TermConcept(Base):
    __tablename__ = "term_concepts"

    term_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("terms.id", ondelete="CASCADE"), primary_key=True)
    concept_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("concepts.id", ondelete="CASCADE"), primary_key=True)


class Term(UUIDPrimaryKeyMixin, TimestampMixin, CreatedByMixin, Base):
    __tablename__ = "terms"
    __table_args__ = (
        Index("ix_terms_surface_form", "surface_form"),
        Index("ix_terms_language", "language"),
    )

    surface_form: Mapped[str] = mapped_column(String(500), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    field_hint: Mapped[str | None] = mapped_column(String(100), nullable=True)

    concepts = relationship("Concept", secondary="term_concepts", back_populates="terms")
