from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class CanonicalBusinessEntity(Base):
    """Organización empresarial única (identidad canónica)."""

    __tablename__ = "canonical_business_entity"
    __table_args__ = (
        Index("ix_cbe_normalized_name", "normalized_name"),
        Index("ix_cbe_primary_rfc", "primary_rfc"),
    )

    canonical_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_rfc: Mapped[str | None] = mapped_column(String(20), nullable=True)
    alias_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class BusinessEntityResolution(Base):
    """Puente 1:1 entre entidad estructural y entidad canónica."""

    __tablename__ = "business_entity_resolution"
    __table_args__ = (
        UniqueConstraint("entity_id", name="uq_ber_entity_id"),
        Index("ix_ber_canonical_id", "canonical_id"),
    )

    resolution_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("business_entity_master.entity_id", ondelete="CASCADE"),
        nullable=False,
    )
    canonical_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("canonical_business_entity.canonical_id", ondelete="CASCADE"),
        nullable=False,
    )
    resolution_rule: Mapped[str] = mapped_column(String(80), nullable=False)
    resolution_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class CanonicalEntitySuggestion(Base):
    """Sugerencia de identidad compartida — no aplica merge automático."""

    __tablename__ = "canonical_entity_suggestion"
    __table_args__ = (
        UniqueConstraint(
            "source_entity_id",
            "candidate_entity_id",
            "rule_used",
            name="uq_ces_source_candidate_rule",
        ),
        Index("ix_ces_status", "status"),
        Index("ix_ces_score", "score"),
    )

    suggestion_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_entity_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("business_entity_master.entity_id", ondelete="CASCADE"),
        nullable=False,
    )
    candidate_entity_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("business_entity_master.entity_id", ondelete="CASCADE"),
        nullable=False,
    )
    rule_used: Mapped[str] = mapped_column(String(80), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
