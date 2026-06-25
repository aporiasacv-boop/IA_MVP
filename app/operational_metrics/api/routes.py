from fastapi import APIRouter, Depends

from app.api.deps import get_operational_metrics_service_dep
from app.operational_metrics.schemas import (
    FinOpsCostsResponse,
    FinOpsForecastResponse,
    FinOpsHealthResponse,
    FinOpsOverviewResponse,
    FinOpsProvidersResponse,
    FinOpsSavingsResponse,
    FinOpsTrendsResponse,
)
from app.operational_metrics.service import OperationalMetricsService

router = APIRouter(prefix="/api/finops", tags=["finops"])


@router.get("/overview", response_model=FinOpsOverviewResponse)
def finops_overview(
    service: OperationalMetricsService = Depends(get_operational_metrics_service_dep),
) -> FinOpsOverviewResponse:
    return service.overview()


@router.get("/costs", response_model=FinOpsCostsResponse)
def finops_costs(
    service: OperationalMetricsService = Depends(get_operational_metrics_service_dep),
) -> FinOpsCostsResponse:
    return service.costs()


@router.get("/providers", response_model=FinOpsProvidersResponse)
def finops_providers(
    service: OperationalMetricsService = Depends(get_operational_metrics_service_dep),
) -> FinOpsProvidersResponse:
    return service.providers()


@router.get("/forecast", response_model=FinOpsForecastResponse)
def finops_forecast(
    service: OperationalMetricsService = Depends(get_operational_metrics_service_dep),
) -> FinOpsForecastResponse:
    return service.forecast()


@router.get("/savings", response_model=FinOpsSavingsResponse)
def finops_savings(
    service: OperationalMetricsService = Depends(get_operational_metrics_service_dep),
) -> FinOpsSavingsResponse:
    return service.savings()


@router.get("/trends", response_model=FinOpsTrendsResponse)
def finops_trends(
    service: OperationalMetricsService = Depends(get_operational_metrics_service_dep),
) -> FinOpsTrendsResponse:
    return service.trends()


@router.get("/health", response_model=FinOpsHealthResponse, include_in_schema=False)
def finops_health(
    service: OperationalMetricsService = Depends(get_operational_metrics_service_dep),
) -> FinOpsHealthResponse:
    return service.health()
