from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class BusinessOntologyType(Base):
    """Entrada de taxonomía editable: Identity, Role, Nature o Behavior."""

    __tablename__ = "business_ontology_type"
    __table_args__ = (
        UniqueConstraint("concept_category", "type_code", name="uq_bot_category_code"),
        Index("ix_bot_concept_category", "concept_category"),
    )

    type_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    concept_category: Mapped[str] = mapped_column(String(20), nullable=False)
    type_code: Mapped[str] = mapped_column(String(60), nullable=False)
    type_label: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class BusinessOntologyRule(Base):
    """Regla determinística de clasificación."""

    __tablename__ = "business_ontology_rule"
    __table_args__ = (
        UniqueConstraint("rule_code", name="uq_bor_rule_code"),
        Index("ix_bor_concept_category", "concept_category"),
    )

    rule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    rule_code: Mapped[str] = mapped_column(String(80), nullable=False)
    concept_category: Mapped[str] = mapped_column(String(20), nullable=False)
    target_type_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("business_ontology_type.type_id", ondelete="CASCADE"),
        nullable=False,
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    conditions_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_weight: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=Decimal("0.8000"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class BusinessOntologyAssignment(Base):
    """Sugerencia de clasificación — nunca se aplica automáticamente."""

    __tablename__ = "business_ontology_assignment"
    __table_args__ = (
        UniqueConstraint(
            "canonical_id",
            "concept_category",
            "type_id",
            "rule_code",
            name="uq_boa_canonical_category_type_rule",
        ),
        Index("ix_boa_status", "status"),
        Index("ix_boa_canonical_id", "canonical_id"),
        Index("ix_boa_concept_category", "concept_category"),
    )

    assignment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canonical_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("canonical_business_entity.canonical_id", ondelete="CASCADE"),
        nullable=False,
    )
    concept_category: Mapped[str] = mapped_column(String(20), nullable=False)
    type_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("business_ontology_type.type_id", ondelete="CASCADE"),
        nullable=False,
    )
    rule_code: Mapped[str] = mapped_column(String(80), nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
