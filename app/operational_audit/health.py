from app.operational_audit.schemas import AuditOverviewResponse


class OperationalAuditHealthError(Exception):
    pass


def validate_overview_health(overview: AuditOverviewResponse) -> dict:
    if overview.total_requests < 0:
        raise OperationalAuditHealthError("total_requests no puede ser negativo")
    if overview.total_successes < 0 or overview.total_failures < 0:
        raise OperationalAuditHealthError("métricas de éxito/fallo no pueden ser negativas")
    if overview.total_successes + overview.total_failures != overview.total_requests:
        raise OperationalAuditHealthError(
            "total_successes + total_failures debe igualar total_requests"
        )

    pct_sum = round(
        overview.business_pipeline_pct
        + overview.memory_pct
        + overview.clarification_pct
        + overview.capability_pct
        + overview.fallback_pct
        + overview.legacy_pct,
        2,
    )
    if overview.total_requests > 0 and abs(pct_sum - 100.0) > 0.5:
        raise OperationalAuditHealthError(f"Porcentajes inconsistentes: {pct_sum}")

    if not 0.0 <= overview.coverage_score <= 100.0:
        raise OperationalAuditHealthError("coverage_score fuera de rango")
    if not 0.0 <= overview.coverage_gap_score <= 100.0:
        raise OperationalAuditHealthError("coverage_gap_score fuera de rango")

    return {
        "total_requests": overview.total_requests,
        "pct_sum": pct_sum,
        "coverage_score": overview.coverage_score,
        "coverage_gap_score": overview.coverage_gap_score,
    }
