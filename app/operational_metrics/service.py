from sqlalchemy.orm import Session

from app.operational_metrics.aggregator import OperationalMetricsAggregator
from app.operational_metrics.collector import build_operational_record
from app.operational_metrics.forecast_engine import ForecastEngine
from app.operational_metrics.health import build_finops_health
from app.operational_metrics.metrics import get_operational_finops_metrics
from app.operational_metrics.repository import OperationalMetricsRepository
from app.operational_metrics.schemas import (
    FinOpsCostsResponse,
    FinOpsForecastResponse,
    FinOpsOverviewResponse,
    FinOpsProvidersResponse,
    FinOpsSavingsResponse,
    FinOpsTrendsResponse,
    OperationalQueryRecord,
)
from app.schemas.hybrid_chat import HybridChatRequest, HybridChatResult


class OperationalMetricsService:
    def __init__(self, repository: OperationalMetricsRepository) -> None:
        self._repository = repository

    def record_query(
        self,
        *,
        request: HybridChatRequest,
        result: HybridChatResult,
        wall_time_ms: float,
        user_id: str | None = None,
        channel: str = "hybrid",
    ) -> OperationalQueryRecord:
        record = build_operational_record(
            request=request,
            result=result,
            wall_time_ms=wall_time_ms,
            user_id=user_id,
            channel=channel,
        )
        saved = self._repository.save(record)
        get_operational_finops_metrics().record(saved)
        return saved

    def overview(self) -> FinOpsOverviewResponse:
        return OperationalMetricsAggregator(self._repository.list_records()).overview()

    def costs(self) -> FinOpsCostsResponse:
        return OperationalMetricsAggregator(self._repository.list_records()).costs()

    def providers(self) -> FinOpsProvidersResponse:
        return OperationalMetricsAggregator(self._repository.list_records()).providers()

    def savings(self) -> FinOpsSavingsResponse:
        return OperationalMetricsAggregator(self._repository.list_records()).savings()

    def trends(self) -> FinOpsTrendsResponse:
        return OperationalMetricsAggregator(self._repository.list_records()).trends()

    def forecast(self) -> FinOpsForecastResponse:
        records = self._repository.list_records()
        return ForecastEngine.from_records(records).build_forecast()

    def health(self):
        return build_finops_health(self._repository)


_service: OperationalMetricsService | None = None


def get_operational_metrics_service(session: Session | None = None) -> OperationalMetricsService:
    global _service
    if session is not None:
        return OperationalMetricsService(OperationalMetricsRepository(session))
    if _service is None:
        _service = OperationalMetricsService(OperationalMetricsRepository())
    return _service


def reset_operational_metrics_service() -> None:
    global _service
    _service = None


def record_hybrid_operational_query(
    request: HybridChatRequest,
    result: HybridChatResult,
    wall_time_ms: float,
    *,
    user_id: str | None = None,
) -> OperationalQueryRecord:
    return get_operational_metrics_service().record_query(
        request=request,
        result=result,
        wall_time_ms=wall_time_ms,
        user_id=user_id,
    )
