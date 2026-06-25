from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func, select, text
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.database.database import Base
from app.observability.performance_metrics import PerformanceMetrics


class PerformanceMetricRecord(Base):
    __tablename__ = "performance_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    handled_by: Mapped[str] = mapped_column(String(50), nullable=False)
    operation_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    entity_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    intent_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    planner_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    executor_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    database_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    legacy_chat_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    ollama_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    query_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    suggested_questions_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    route_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    response_success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    deterministic_resolution: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    used_ai: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PerformanceMetricsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, metrics: PerformanceMetrics) -> PerformanceMetrics:
        record = PerformanceMetricRecord(
            request_id=metrics.request_id,
            question=metrics.question,
            handled_by=metrics.handled_by,
            operation_time_ms=metrics.operation_time_ms,
            entity_time_ms=metrics.entity_time_ms,
            intent_time_ms=metrics.intent_time_ms,
            planner_time_ms=metrics.planner_time_ms,
            executor_time_ms=metrics.executor_time_ms,
            database_time_ms=metrics.database_time_ms,
            response_time_ms=metrics.response_time_ms,
            legacy_chat_time_ms=metrics.legacy_chat_time_ms,
            ollama_time_ms=metrics.ollama_time_ms,
            total_time_ms=metrics.total_time_ms,
            query_type=metrics.query_type,
            success=metrics.success,
            suggested_questions_count=metrics.suggested_questions_count,
            route_type=metrics.route_type,
            response_success=metrics.response_success,
            deterministic_resolution=metrics.deterministic_resolution,
            used_ai=metrics.used_ai,
            created_at=metrics.created_at,
        )
        self.session.add(record)
        self.session.commit()
        return metrics

    def get_summary(self) -> dict:
        row = self.session.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total_requests,
                    COUNT(*) FILTER (WHERE handled_by = 'business_pipeline') AS business_pipeline_requests,
                    COUNT(*) FILTER (WHERE handled_by = 'legacy_chat') AS legacy_chat_requests,
                    COUNT(*) FILTER (WHERE handled_by = 'guided_fallback') AS guided_fallback_requests,
                    COUNT(*) FILTER (WHERE handled_by = 'capability_discovery') AS capability_discovery_requests,
                    COUNT(*) FILTER (WHERE handled_by = 'slot_clarification') AS slot_clarification_requests,
                    COUNT(*) FILTER (WHERE handled_by = 'conversation_memory') AS conversation_memory_requests,
                    COUNT(*) FILTER (
                        WHERE COALESCE(suggested_questions_count, 0) > 0
                    ) AS suggested_questions_generated,
                    COALESCE(AVG(suggested_questions_count), 0) AS average_suggestions_per_response,
                    COALESCE(AVG(total_time_ms), 0) AS avg_total_time_ms,
                    AVG(database_time_ms) AS avg_database_time_ms,
                    AVG(ollama_time_ms) AS avg_ollama_time_ms
                FROM performance_metrics
                """
            )
        ).mappings().one()
        return {
            "total_requests": int(row["total_requests"]),
            "business_pipeline_requests": int(row["business_pipeline_requests"]),
            "legacy_chat_requests": int(row["legacy_chat_requests"]),
            "guided_fallback_requests": int(row["guided_fallback_requests"]),
            "capability_discovery_requests": int(row["capability_discovery_requests"]),
            "slot_clarification_requests": int(row["slot_clarification_requests"]),
            "conversation_memory_requests": int(row["conversation_memory_requests"]),
            "suggested_questions_generated": int(row["suggested_questions_generated"]),
            "average_suggestions_per_response": round(
                float(row["average_suggestions_per_response"]),
                4,
            ),
            "avg_total_time_ms": round(float(row["avg_total_time_ms"]), 4),
            "avg_database_time_ms": (
                round(float(row["avg_database_time_ms"]), 4)
                if row["avg_database_time_ms"] is not None
                else None
            ),
            "avg_ollama_time_ms": (
                round(float(row["avg_ollama_time_ms"]), 4)
                if row["avg_ollama_time_ms"] is not None
                else None
            ),
        }

    def get_top_queries(self, limit: int = 10) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT question, COUNT(*) AS count
                FROM performance_metrics
                GROUP BY question
                ORDER BY count DESC, question ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [
            {"question": row["question"], "count": int(row["count"])}
            for row in rows
        ]

    def get_performance(self) -> dict:
        percentile_row = self.session.execute(
            text(
                """
                SELECT
                    COALESCE(
                        percentile_cont(0.5) WITHIN GROUP (ORDER BY total_time_ms),
                        0
                    ) AS p50_total_time_ms,
                    COALESCE(
                        percentile_cont(0.95) WITHIN GROUP (ORDER BY total_time_ms),
                        0
                    ) AS p95_total_time_ms,
                    COALESCE(
                        percentile_cont(0.99) WITHIN GROUP (ORDER BY total_time_ms),
                        0
                    ) AS p99_total_time_ms
                FROM performance_metrics
                """
            )
        ).mappings().one()

        averages_row = self.session.execute(
            text(
                """
                SELECT
                    AVG(operation_time_ms) AS operation_time_ms,
                    AVG(entity_time_ms) AS entity_time_ms,
                    AVG(intent_time_ms) AS intent_time_ms,
                    AVG(planner_time_ms) AS planner_time_ms,
                    AVG(executor_time_ms) AS executor_time_ms,
                    AVG(database_time_ms) AS database_time_ms,
                    AVG(response_time_ms) AS response_time_ms,
                    AVG(legacy_chat_time_ms) AS legacy_chat_time_ms,
                    AVG(ollama_time_ms) AS ollama_time_ms,
                    AVG(total_time_ms) AS total_time_ms
                FROM performance_metrics
                """
            )
        ).mappings().one()

        stage_fields = (
            "operation_time_ms",
            "entity_time_ms",
            "intent_time_ms",
            "planner_time_ms",
            "executor_time_ms",
            "database_time_ms",
            "response_time_ms",
            "legacy_chat_time_ms",
            "ollama_time_ms",
            "total_time_ms",
        )
        averages = {
            field: (
                round(float(averages_row[field]), 4)
                if averages_row[field] is not None
                else None
            )
            for field in stage_fields
        }

        return {
            "p50_total_time_ms": round(float(percentile_row["p50_total_time_ms"]), 4),
            "p95_total_time_ms": round(float(percentile_row["p95_total_time_ms"]), 4),
            "p99_total_time_ms": round(float(percentile_row["p99_total_time_ms"]), 4),
            "averages": averages,
        }

    def get_routing_metrics(self, *, path_limit: int = 10) -> dict:
        distribution_rows = self.session.execute(
            text(
                """
                SELECT
                    handled_by,
                    COUNT(*) AS count,
                    COALESCE(AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END), 0) AS success_rate
                FROM performance_metrics
                GROUP BY handled_by
                ORDER BY count DESC, handled_by ASC
                """
            )
        ).mappings().all()

        path_rows = self.session.execute(
            text(
                """
                SELECT
                    handled_by,
                    COALESCE(query_type, 'NONE') AS query_type,
                    COUNT(*) AS count
                FROM performance_metrics
                GROUP BY handled_by, COALESCE(query_type, 'NONE')
                ORDER BY count DESC, handled_by ASC, query_type ASC
                LIMIT :limit
                """
            ),
            {"limit": path_limit},
        ).mappings().all()

        handled_by_distribution = [
            {
                "handled_by": row["handled_by"],
                "count": int(row["count"]),
                "success_rate": round(float(row["success_rate"]), 4),
            }
            for row in distribution_rows
        ]
        success_rate_by_handled_by = {
            item["handled_by"]: item["success_rate"]
            for item in handled_by_distribution
        }
        top_paths = [
            {
                "handled_by": row["handled_by"],
                "query_type": row["query_type"],
                "count": int(row["count"]),
            }
            for row in path_rows
        ]

        return {
            "handled_by_distribution": handled_by_distribution,
            "success_rate_by_handled_by": success_rate_by_handled_by,
            "top_paths": top_paths,
        }

    def count_all(self) -> int:
        return self.session.scalar(select(func.count()).select_from(PerformanceMetricRecord)) or 0
