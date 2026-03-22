from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.schemas.common import ProposalStatus, ProposalType


class Proposal(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "proposals"

    proposal_type: Mapped[ProposalType] = mapped_column(Enum(ProposalType, name="proposal_type_enum", native_enum=False), nullable=False)
    proposed_by_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("actors.id", ondelete="RESTRICT"), nullable=False)
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus, name="proposal_status_enum", native_enum=False), nullable=False, default=ProposalStatus.PENDING)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("actors.id", ondelete="SET NULL"), nullable=True)

    proposed_by = relationship("Actor", foreign_keys=[proposed_by_id], lazy="joined")
    reviewed_by = relationship("Actor", foreign_keys=[reviewed_by_id], lazy="joined")
    reviews = relationship("Review", back_populates="proposal")
