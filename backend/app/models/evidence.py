from __future__ import annotations

from sqlalchemy import Enum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedByMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.schemas.common import EvidenceType, Reliability


class Evidence(UUIDPrimaryKeyMixin, TimestampMixin, CreatedByMixin, Base):
    __tablename__ = "evidence"
    __table_args__ = (
        Index("ix_evidence_evidence_type", "evidence_type"),
        Index("ix_evidence_reliability", "reliability"),
    )

    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType, name="evidence_type_enum", native_enum=False),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    reliability: Mapped[Reliability] = mapped_column(
        Enum(Reliability, name="reliability_enum", native_enum=False),
        nullable=False,
        default=Reliability.UNVERIFIED,
    )

    claim_links = relationship("ClaimEvidence", back_populates="evidence")
