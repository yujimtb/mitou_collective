from __future__ import annotations

import uuid

from sqlalchemy import Enum, Float, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.schemas.common import ConnectionType, ProposalStatus


class CrossFieldConnection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cross_field_connections"

    source_claim_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    target_claim_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    connection_type: Mapped[ConnectionType] = mapped_column(Enum(ConnectionType, name="connection_type_enum", native_enum=False), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    proposal_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("proposals.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus, name="connection_status_enum", native_enum=False), nullable=False, default=ProposalStatus.PENDING)

    source_claim = relationship("Claim", foreign_keys=[source_claim_id])
    target_claim = relationship("Claim", foreign_keys=[target_claim_id])
    proposal = relationship("Proposal")
