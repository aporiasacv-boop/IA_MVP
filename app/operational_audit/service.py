import csv
import io
import json
from datetime import datetime, timezone

from app.guided_fallback.v2.metrics import GuidedFallbackV2Metrics
from app.operational_audit.formulas import coverage_gap_score, coverage_score, pct
from app.operational_audit.health import validate_overview_health
from app.operational_audit.repository import OperationalAuditRepository
from app.operational_audit.schemas import (
    AdoptionMetricsResponse,
    AuditOverviewResponse,
    AuditReportResponse,
    CoverageGapItem,
    CoverageGapsExportResponse,
    DomainFallbackMetricsResponse,
    TopFailureItem,
    TopRouteItem,
)


class OperationalAuditService:
    def __init__(self, repository: OperationalAuditRepository) -> None:
        self._repository = repository

    def get_overview(self) -> AuditOverviewResponse:
        counts = self._repository.get_overview_counts()
        total = int(counts["total_requests"])
        deterministic = (
            int(counts["business_pipeline"])
            + int(counts["slot_clarification"])
            + int(counts["conversation_memory"])
            + int(counts["capability_discovery"])
            + int(counts["guided_fallback"])
        )
        success_rate = float(counts["success_rate"])
        legacy = int(counts["legacy_chat"])
        fallback = int(counts["guided_fallback"])

        overview = AuditOverviewResponse(
            total_requests=total,
            total_successes=int(counts["total_successes"]),
            total_failures=int(counts["total_failures"]),
            business_pipeline_pct=pct(int(counts["business_pipeline"]), total),
            memory_pct=pct(int(counts["conversation_memory"]), total),
            clarification_pct=pct(int(counts["slot_clarification"]), total),
            capability_pct=pct(int(counts["capability_discovery"]), total),
            fallback_pct=pct(fallback, total),
            legacy_pct=pct(legacy, total),
            coverage_score=coverage_score(
                deterministic_count=deterministic,
                total=total,
                success_rate=success_rate,
            ),
            coverage_gap_score=coverage_gap_score(
                legacy_count=legacy,
                fallback_count=fallback,
                total=total,
            ),
        )
        return overview

    def get_coverage_gaps(self, *, limit: int = 50) -> list[CoverageGapItem]:
        rows = self._repository.get_coverage_gaps(limit=limit)
        return [CoverageGapItem(**row) for row in rows]

    def get_top_routes(self, *, limit: int = 20) -> list[TopRouteItem]:
        rows = self._repository.get_top_routes(limit=limit)
        total = self.get_overview().total_requests
        return [
            TopRouteItem(
                route=row["route"],
                count=row["count"],
                percentage=pct(row["count"], total),
            )
            for row in rows
        ]

    def get_top_failures(self, *, limit: int = 50) -> list[TopFailureItem]:
        rows = self._repository.get_top_failures(limit=limit)
        return [TopFailureItem(**row) for row in rows]

    def get_adoption(self) -> AdoptionMetricsResponse:
        counts = self._repository.get_adoption_counts()
        return AdoptionMetricsResponse(**counts)

    def get_domain_fallback_metrics(self) -> DomainFallbackMetricsResponse:
        snapshot = GuidedFallbackV2Metrics.snapshot()
        return DomainFallbackMetricsResponse(**snapshot)

    def get_report(self) -> AuditReportResponse:
        return AuditReportResponse(
            overview=self.get_overview(),
            domain_fallback=self.get_domain_fallback_metrics(),
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def export_coverage_gaps_json(self, *, limit: int = 500) -> CoverageGapsExportResponse:
        items = self.get_coverage_gaps(limit=limit)
        overview = self.get_overview()
        return CoverageGapsExportResponse(
            items=items,
            coverage_gap_score=overview.coverage_gap_score,
            exported_at=datetime.now(timezone.utc).isoformat(),
        )

    def export_coverage_gaps_csv(self, *, limit: int = 500) -> str:
        items = self.get_coverage_gaps(limit=limit)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["question", "count", "route"])
        for item in items:
            writer.writerow([item.question, item.count, item.route])
        return buffer.getvalue()

    def validate_health(self) -> dict:
        overview = self.get_overview()
        return validate_overview_health(overview)

    def export_coverage_gaps_json_text(self, *, limit: int = 500) -> str:
        payload = self.export_coverage_gaps_json(limit=limit)
        return json.dumps(payload.model_dump(), ensure_ascii=False, indent=2)
