from app.operational_metrics.metrics import get_operational_finops_metrics
from app.operational_metrics.repository import OperationalMetricsRepository
from app.operational_metrics.schemas import FinOpsHealthResponse


def build_finops_health(repository: OperationalMetricsRepository) -> FinOpsHealthResponse:
    records = repository.list_records()
    metrics = get_operational_finops_metrics()
    last = records[-1].timestamp if records else None
    real_ratio = 0.0
    if metrics.records_total > 0:
        real_ratio = round(metrics.real_token_records / metrics.records_total, 4)
    return FinOpsHealthResponse(
        status="ok" if records else "degraded",
        records_stored=len(records),
        last_record_at=last,
        real_token_ratio=real_ratio,
        data_source="operational_query_metrics",
    )
