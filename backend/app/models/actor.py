from __future__ import annotations

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.schemas.common import ActorType, TrustLevel


class Actor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "actors"

    actor_type: Mapped[ActorType] = mapped_column(
        Enum(ActorType, name="actor_type_enum", native_enum=False),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    trust_level: Mapped[TrustLevel] = mapped_column(
        Enum(TrustLevel, name="trust_level_enum", native_enum=False),
        nullable=False,
        default=TrustLevel.CONTRIBUTOR,
    )
    agent_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
