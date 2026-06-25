from fastapi import APIRouter, Depends, Query

from app.api.deps import get_business_analytics_service
from app.business_analytics.schemas import (
    CoverageAnalyticsResponse,
    CoverageReportResponse,
    FinancialAnalyticsResponse,
    PerformanceAnalyticsResponse,
    TopQueryAnalyticsItem,
)
from app.business_analytics.service import BusinessAnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["business-analytics"])


@router.get("/coverage", response_model=CoverageAnalyticsResponse)
def get_coverage_analytics(
    service: BusinessAnalyticsService = Depends(get_business_analytics_service),
) -> CoverageAnalyticsResponse:
    return service.get_coverage()


@router.get("/performance", response_model=PerformanceAnalyticsResponse)
def get_performance_analytics(
    service: BusinessAnalyticsService = Depends(get_business_analytics_service),
) -> PerformanceAnalyticsResponse:
    return service.get_performance()


@router.get("/financial", response_model=FinancialAnalyticsResponse)
def get_financial_analytics(
    service: BusinessAnalyticsService = Depends(get_business_analytics_service),
) -> FinancialAnalyticsResponse:
    return service.get_financial()


@router.get("/top-queries", response_model=list[TopQueryAnalyticsItem])
def get_top_queries_analytics(
    limit: int = Query(default=20, ge=1, le=100),
    service: BusinessAnalyticsService = Depends(get_business_analytics_service),
) -> list[TopQueryAnalyticsItem]:
    return service.get_top_queries(limit=limit)


@router.get("/report", response_model=CoverageReportResponse)
def get_coverage_report(
    route_limit: int = Query(default=10, ge=1, le=100),
    service: BusinessAnalyticsService = Depends(get_business_analytics_service),
) -> CoverageReportResponse:
    return service.get_report(route_limit=route_limit)
