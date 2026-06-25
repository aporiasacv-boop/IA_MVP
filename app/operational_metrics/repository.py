from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy import select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.database.database import Base
from app.operational_metrics.schemas import OperationalQueryRecord


class OperationalQueryMetricRecord(Base):
    __tablename__ = "operational_query_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    handled_by: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False, default="hybrid")
    query_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verb: Mapped[str | None] = mapped_column(String(50), nullable=True)
    intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    token_source: Mapped[str] = mapped_column(String(20), nullable=False, default="none")
    cache_hit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    knowledge_hit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    pipeline_hit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    executive_reasoning: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    llm_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    llm_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cost_mxn: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avoided_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


_memory_store: list[OperationalQueryRecord] = []


def reset_operational_memory_store() -> None:
    global _memory_store
    _memory_store = []


class OperationalMetricsRepository:
    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def save(self, record: OperationalQueryRecord) -> OperationalQueryRecord:
        _memory_store.append(record)
        if len(_memory_store) > 50000:
            del _memory_store[:-50000]
        if self._session is not None:
            self._session.add(
                OperationalQueryMetricRecord(
                    request_id=record.request_id,
                    timestamp=record.timestamp,
                    session_id=record.session_id,
                    handled_by=record.handled_by,
                    provider=record.provider,
                    model=record.model,
                    user_id=record.user_id,
                    channel=record.channel,
                    query_type=record.query_type,
                    verb=record.verb,
                    intent=record.intent,
                    response_time_ms=record.response_time_ms,
                    input_tokens=record.input_tokens,
                    output_tokens=record.output_tokens,
                    total_tokens=record.total_tokens,
                    estimated_tokens=record.estimated_tokens,
                    token_source=record.token_source,
                    cache_hit=record.cache_hit,
                    knowledge_hit=record.knowledge_hit,
                    pipeline_hit=record.pipeline_hit,
                    executive_reasoning=record.executive_reasoning,
                    llm_used=record.llm_used,
                    llm_provider=record.llm_provider,
                    llm_model=record.llm_model,
                    success=record.success,
                    confidence=record.confidence,
                    cost_usd=record.cost_usd,
                    cost_mxn=record.cost_mxn,
                    avoided_cost_usd=record.avoided_cost_usd,
                )
            )
            try:
                self._session.commit()
            except Exception:
                self._session.rollback()
        return record

    def list_records(self) -> list[OperationalQueryRecord]:
        if self._session is not None:
            try:
                rows = self._session.scalars(
                    select(OperationalQueryMetricRecord).order_by(
                        OperationalQueryMetricRecord.timestamp.desc()
                    )
                ).all()
                if rows:
                    return [self._to_schema(row) for row in rows]
            except Exception:
                pass
        return list(_memory_store)

    @staticmethod
    def _to_schema(row: OperationalQueryMetricRecord) -> OperationalQueryRecord:
        return OperationalQueryRecord(
            request_id=row.request_id,
            timestamp=row.timestamp,
            session_id=row.session_id,
            handled_by=row.handled_by,
            provider=row.provider,
            model=row.model,
            user_id=row.user_id,
            channel=row.channel,
            query_type=row.query_type,
            verb=row.verb,
            intent=row.intent,
            response_time_ms=row.response_time_ms,
            input_tokens=row.input_tokens,
            output_tokens=row.output_tokens,
            total_tokens=row.total_tokens,
            estimated_tokens=row.estimated_tokens,
            token_source=row.token_source,
            cache_hit=row.cache_hit,
            knowledge_hit=row.knowledge_hit,
            pipeline_hit=row.pipeline_hit,
            executive_reasoning=row.executive_reasoning,
            llm_used=row.llm_used,
            llm_provider=row.llm_provider,
            llm_model=row.llm_model,
            success=row.success,
            confidence=row.confidence,
            cost_usd=row.cost_usd,
            cost_mxn=row.cost_mxn,
            avoided_cost_usd=row.avoided_cost_usd,
        )
