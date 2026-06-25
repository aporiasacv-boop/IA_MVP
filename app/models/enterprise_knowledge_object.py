from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class EnterpriseKnowledgeObject(Base):
    """Objeto de conocimiento empresarial persistido por entidad canónica."""

    __tablename__ = "enterprise_knowledge_object"
    __table_args__ = (
        UniqueConstraint("canonical_id", name="uq_eko_canonical_id"),
        Index("ix_eko_completeness", "completeness"),
        Index("ix_eko_average_confidence", "average_confidence"),
        Index("ix_eko_built_at", "built_at"),
    )

    knowledge_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canonical_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("canonical_business_entity.canonical_id", ondelete="CASCADE"),
        nullable=False,
    )
    knowledge_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    completeness: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=0)
    average_confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=0)
    built_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
