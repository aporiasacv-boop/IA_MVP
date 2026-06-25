from sqlalchemy.orm import Session

from app.observability.metrics_repository import PerformanceMetricsRepository
from app.observability.performance_metrics import (
    PerformanceCollector,
    PerformanceMetrics,
    get_database_time,
    reset_database_time,
    set_active_collector,
)


class PerformanceTracker:
    def __init__(self, session: Session) -> None:
        self._repository = PerformanceMetricsRepository(session)

    def start_request(self, question: str) -> PerformanceCollector:
        reset_database_time()
        collector = PerformanceCollector(question=question)
        set_active_collector(collector)
        return collector

    def record_stage(self, collector: PerformanceCollector, stage: str, duration_ms: float) -> None:
        collector.record_stage(stage, duration_ms)

    def finish_request(
        self,
        collector: PerformanceCollector,
        *,
        handled_by: str,
        success: bool,
        query_type: str | None,
        suggested_questions_count: int | None = None,
    ) -> PerformanceMetrics:
        metrics = collector.finalize(
            handled_by=handled_by,
            success=success,
            query_type=query_type,
            database_time_ms=get_database_time() or None,
            suggested_questions_count=suggested_questions_count,
        )
        set_active_collector(None)
        return metrics

    def persist(self, metrics: PerformanceMetrics) -> PerformanceMetrics:
        return self._repository.save(metrics)
