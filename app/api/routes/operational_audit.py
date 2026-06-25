from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse, Response

from app.api.deps import get_operational_audit_service
from app.operational_audit.schemas import (
    AdoptionMetricsResponse,
    AuditOverviewResponse,
    AuditReportResponse,
    CoverageGapItem,
    DomainFallbackMetricsResponse,
    TopFailureItem,
    TopRouteItem,
)
from app.operational_audit.service import OperationalAuditService

router = APIRouter(prefix="/api/audit", tags=["operational-audit"])


@router.get("/overview", response_model=AuditOverviewResponse)
def get_audit_overview(
    service: OperationalAuditService = Depends(get_operational_audit_service),
) -> AuditOverviewResponse:
    return service.get_overview()


@router.get("/coverage-gaps", response_model=list[CoverageGapItem])
def get_coverage_gaps(
    limit: int = Query(default=50, ge=1, le=500),
    service: OperationalAuditService = Depends(get_operational_audit_service),
) -> list[CoverageGapItem]:
    return service.get_coverage_gaps(limit=limit)


@router.get("/coverage-gaps/export")
def export_coverage_gaps(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    limit: int = Query(default=500, ge=1, le=2000),
    service: OperationalAuditService = Depends(get_operational_audit_service),
) -> Response:
    if format == "csv":
        content = service.export_coverage_gaps_csv(limit=limit)
        return PlainTextResponse(
            content=content,
            media_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="coverage_gaps.csv"',
            },
        )

    content = service.export_coverage_gaps_json_text(limit=limit)
    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition": 'attachment; filename="coverage_gaps.json"',
        },
    )


@router.get("/top-routes", response_model=list[TopRouteItem])
def get_top_routes(
    limit: int = Query(default=20, ge=1, le=100),
    service: OperationalAuditService = Depends(get_operational_audit_service),
) -> list[TopRouteItem]:
    return service.get_top_routes(limit=limit)


@router.get("/top-failures", response_model=list[TopFailureItem])
def get_top_failures(
    limit: int = Query(default=50, ge=1, le=500),
    service: OperationalAuditService = Depends(get_operational_audit_service),
) -> list[TopFailureItem]:
    return service.get_top_failures(limit=limit)


@router.get("/adoption", response_model=AdoptionMetricsResponse)
def get_adoption_metrics(
    service: OperationalAuditService = Depends(get_operational_audit_service),
) -> AdoptionMetricsResponse:
    return service.get_adoption()


@router.get("/report", response_model=AuditReportResponse)
def get_audit_report(
    service: OperationalAuditService = Depends(get_operational_audit_service),
) -> AuditReportResponse:
    return service.get_report()
