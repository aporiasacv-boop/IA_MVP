import pytest

from app.operational_audit.health import OperationalAuditHealthError, validate_overview_health
from app.operational_audit.schemas import AuditOverviewResponse


def _overview(**overrides) -> AuditOverviewResponse:
    base = {
        "total_requests": 100,
        "total_successes": 90,
        "total_failures": 10,
        "business_pipeline_pct": 50.0,
        "memory_pct": 10.0,
        "clarification_pct": 10.0,
        "capability_pct": 10.0,
        "fallback_pct": 10.0,
        "legacy_pct": 10.0,
        "coverage_score": 85.0,
        "coverage_gap_score": 20.0,
    }
    base.update(overrides)
    return AuditOverviewResponse(**base)


def test_validate_health_ok() -> None:
    result = validate_overview_health(_overview())
    assert result["pct_sum"] == 100.0


def test_validate_health_rejects_negative_requests() -> None:
    with pytest.raises(OperationalAuditHealthError, match="total_requests"):
        validate_overview_health(_overview(total_requests=-1))


def test_validate_health_rejects_negative_success() -> None:
    with pytest.raises(OperationalAuditHealthError, match="éxito/fallo"):
        validate_overview_health(_overview(total_successes=-1))


def test_validate_health_rejects_mismatched_totals() -> None:
    with pytest.raises(OperationalAuditHealthError, match="debe igualar"):
        validate_overview_health(_overview(total_failures=5))


def test_validate_health_rejects_inconsistent_percentages() -> None:
    with pytest.raises(OperationalAuditHealthError, match="Porcentajes inconsistentes"):
        validate_overview_health(_overview(business_pipeline_pct=30.0))


def test_validate_health_rejects_gap_score_out_of_range() -> None:
    with pytest.raises(OperationalAuditHealthError, match="coverage_gap_score"):
        validate_overview_health(_overview(coverage_gap_score=101.0))


def test_validate_health_zero_requests_skips_pct_sum() -> None:
    result = validate_overview_health(
        _overview(
            total_requests=0,
            total_successes=0,
            total_failures=0,
            business_pipeline_pct=0.0,
            memory_pct=0.0,
            clarification_pct=0.0,
            capability_pct=0.0,
            fallback_pct=0.0,
            legacy_pct=0.0,
            coverage_score=0.0,
            coverage_gap_score=0.0,
        )
    )
    assert result["total_requests"] == 0
