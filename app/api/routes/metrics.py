from fastapi import APIRouter, Depends, Query

from app.api.deps import get_metrics_service
from app.observability.metrics_service import MetricsService
from app.schemas.metrics import (
    MetricsSummaryResponse,
    PerformanceStatsResponse,
    RoutingMetricsResponse,
    TopQueryItem,
)

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get(
    "/summary",
    response_model=MetricsSummaryResponse,
    summary="Resumen agregado de metricas de rendimiento",
)
def get_metrics_summary(
    service: MetricsService = Depends(get_metrics_service),
) -> MetricsSummaryResponse:
    return service.get_summary()


@router.get(
    "/top-queries",
    response_model=list[TopQueryItem],
    summary="Preguntas mas frecuentes",
)
def get_top_queries(
    limit: int = Query(default=10, ge=1, le=100),
    service: MetricsService = Depends(get_metrics_service),
) -> list[TopQueryItem]:
    return service.get_top_queries(limit=limit)


@router.get(
    "/performance",
    response_model=PerformanceStatsResponse,
    summary="Percentiles y promedios por etapa",
)
def get_performance_stats(
    service: MetricsService = Depends(get_metrics_service),
) -> PerformanceStatsResponse:
    return service.get_performance()


@router.get(
    "/routing",
    response_model=RoutingMetricsResponse,
    summary="Distribucion de handled_by, success rate y top paths",
)
def get_routing_metrics(
    path_limit: int = Query(default=10, ge=1, le=100),
    service: MetricsService = Depends(get_metrics_service),
) -> RoutingMetricsResponse:
    return service.get_routing_metrics(path_limit=path_limit)
