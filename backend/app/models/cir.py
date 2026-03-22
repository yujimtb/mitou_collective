from __future__ import annotations

from dataclasses import dataclass
import uuid

from sqlalchemy import ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


@dataclass(slots=True)
class Condition:
    predicate: str
    argument: str
    negated: bool = False


class CIR(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cir"

    claim_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, unique=True)
    context_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    relation: Mapped[str] = mapped_column(String(255), nullable=False)
    object: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    units: Mapped[str | None] = mapped_column(String(100), nullable=True)
    definition_refs: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    claim = relationship("Claim", back_populates="cir")
