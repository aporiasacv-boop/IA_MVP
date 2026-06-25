from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Index, Integer, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class BusinessEntityProfile(Base):
    """Perfil de comportamiento transaccional por entidad canónica."""

    __tablename__ = "business_entity_profile"
    __table_args__ = (
        UniqueConstraint("canonical_id", name="uq_bep_canonical_id"),
        Index("ix_bep_total_movements", "total_movements"),
        Index("ix_bep_last_seen", "last_seen"),
        Index("ix_bep_profile_completeness", "profile_completeness"),
    )

    profile_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canonical_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("canonical_business_entity.canonical_id", ondelete="CASCADE"),
        nullable=False,
    )
    total_movements: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    average_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    first_seen: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_seen: Mapped[date | None] = mapped_column(Date, nullable=True)
    active_months: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    debit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    debit_credit_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    related_accounts_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    related_counterparties_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monthly_distribution: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    currencies: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    journals: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    dimensions_used: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    top_accounts: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    top_counterparties: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    profile_completeness: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=0)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
