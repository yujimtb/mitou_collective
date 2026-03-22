from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedByMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Referent(UUIDPrimaryKeyMixin, TimestampMixin, CreatedByMixin, Base):
    __tablename__ = "referents"

    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    concepts = relationship("Concept", back_populates="referent")
