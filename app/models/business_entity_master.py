from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class BusinessEntityMaster(Base):
    """Catálogo maestro estructural de entidades descubiertas en el diario general."""

    __tablename__ = "business_entity_master"
    __table_args__ = (
        UniqueConstraint(
            "source_system",
            "source_table",
            "source_column",
            "entity_code",
            name="uq_business_entity_source_code",
        ),
        Index("ix_bem_entity_code", "entity_code"),
        Index("ix_bem_classification_status", "classification_status"),
        Index("ix_bem_source_column", "source_column"),
        Index("ix_bem_movement_count", "movement_count"),
    )

    entity_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity_code: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_system: Mapped[str] = mapped_column(String(50), nullable=False)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    source_column: Mapped[str] = mapped_column(String(100), nullable=False)
    movement_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    movement_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    first_seen: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_seen: Mapped[date | None] = mapped_column(Date, nullable=True)
    classification_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    confidence: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
