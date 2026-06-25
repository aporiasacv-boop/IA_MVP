from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class EnterpriseReasoningObject(Base):
    """Objeto de razonamiento empresarial persistido por entidad canónica."""

    __tablename__ = "enterprise_reasoning_object"
    __table_args__ = (
        UniqueConstraint("canonical_id", name="uq_ero_canonical_id"),
        Index("ix_ero_average_confidence", "average_confidence"),
        Index("ix_ero_findings_count", "findings_count"),
        Index("ix_ero_built_at", "built_at"),
    )

    reasoning_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canonical_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("canonical_business_entity.canonical_id", ondelete="CASCADE"),
        nullable=False,
    )
    reasoning_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    average_confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=0)
    findings_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    alerts_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    recommendations_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    built_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
