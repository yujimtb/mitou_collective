from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedByMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Context(UUIDPrimaryKeyMixin, TimestampMixin, CreatedByMixin, Base):
    __tablename__ = "contexts"
    __table_args__ = (Index("ix_contexts_field", "field"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    field: Mapped[str] = mapped_column(String(100), nullable=False)
    assumptions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    parent_context_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("contexts.id", ondelete="SET NULL"),
        nullable=True,
    )

    parent = relationship("Context", remote_side="Context.id", back_populates="children")
    children = relationship("Context", back_populates="parent")
    claim_links = relationship("ClaimContext", back_populates="context")
