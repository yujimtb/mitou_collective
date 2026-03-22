from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedByMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.schemas.common import ClaimType, EvidenceRelationship, TrustStatus


class ClaimContext(Base):
    __tablename__ = "claim_contexts"

    claim_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("claims.id", ondelete="CASCADE"), primary_key=True)
    context_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("contexts.id", ondelete="CASCADE"), primary_key=True)

    claim = relationship("Claim", back_populates="context_links")
    context = relationship("Context", back_populates="claim_links")


class ClaimConcept(Base):
    __tablename__ = "claim_concepts"

    claim_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("claims.id", ondelete="CASCADE"), primary_key=True)
    concept_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("concepts.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="related")

    claim = relationship("Claim", back_populates="concept_links")
    concept = relationship("Concept", back_populates="claim_links")


class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"

    claim_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("claims.id", ondelete="CASCADE"), primary_key=True)
    evidence_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True)
    relationship_type: Mapped[EvidenceRelationship] = mapped_column(
        "relationship",
        Enum(EvidenceRelationship, name="evidence_relationship_enum", native_enum=False),
        nullable=False,
        default=EvidenceRelationship.SUPPORTS,
    )

    claim = relationship("Claim", back_populates="evidence_links")
    evidence = relationship("Evidence", back_populates="claim_links")


class Claim(UUIDPrimaryKeyMixin, TimestampMixin, CreatedByMixin, Base):
    __tablename__ = "claims"
    __table_args__ = (
        Index("ix_claims_claim_type", "claim_type"),
        Index("ix_claims_trust_status", "trust_status"),
    )

    statement: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[ClaimType] = mapped_column(Enum(ClaimType, name="claim_type_enum", native_enum=False), nullable=False)
    trust_status: Mapped[TrustStatus] = mapped_column(Enum(TrustStatus, name="trust_status_enum", native_enum=False), nullable=False, default=TrustStatus.TENTATIVE)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    context_links = relationship("ClaimContext", back_populates="claim", cascade="all, delete-orphan")
    concept_links = relationship("ClaimConcept", back_populates="claim", cascade="all, delete-orphan")
    evidence_links = relationship("ClaimEvidence", back_populates="claim", cascade="all, delete-orphan")
    cir = relationship("CIR", back_populates="claim", uselist=False, cascade="all, delete-orphan")
