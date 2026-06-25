import pytest

from app.coverage_recovery.classifier import RecoveryCategory, classify_recovery_question
from app.coverage_recovery.health import CoverageRecoveryHealthError, validate_coverage_recovery_health
from app.coverage_recovery.metrics import (
    CoverageRecoveryMetricsService,
    coverage_recovery_metrics,
)
from app.coverage_recovery.patterns import (
    CAPABILITY_DISCOVERY_QUERIES,
    DATA_COVERAGE_QUERIES,
    DATASET_INFO_QUERIES,
)
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    coverage_recovery_metrics.coverage_recovery_hits = 0
    coverage_recovery_metrics.coverage_recovery_misses = 0


@pytest.mark.parametrize("question", DATA_COVERAGE_QUERIES)
def test_classify_data_coverage_questions(question: str) -> None:
    assert classify_recovery_question(question) == RecoveryCategory.DATA_COVERAGE


@pytest.mark.parametrize("question", DATASET_INFO_QUERIES)
def test_classify_dataset_info_questions(question: str) -> None:
    assert classify_recovery_question(question) == RecoveryCategory.DATASET_INFO


@pytest.mark.parametrize("question", CAPABILITY_DISCOVERY_QUERIES)
def test_classify_capability_discovery_questions(question: str) -> None:
    assert classify_recovery_question(question) == RecoveryCategory.CAPABILITY_DISCOVERY


def test_classify_unknown_question_returns_none() -> None:
    assert classify_recovery_question("¿Cuántos clientes existen?") is None


def test_validate_coverage_recovery_health_passes() -> None:
    result = validate_coverage_recovery_health()
    assert result["status"] == "ok"
    assert result["data_coverage_queries"] == 7


def test_record_hit_for_data_coverage() -> None:
    result = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="ok",
        metadata={"query_type": "DATA_COVERAGE"},
    )
    CoverageRecoveryMetricsService.record_outcome("¿Qué fechas cubren los datos?", result)
    snapshot = CoverageRecoveryMetricsService.snapshot()
    assert snapshot["coverage_recovery_hits"] == 1
    assert snapshot["coverage_recovery_misses"] == 0


def test_record_miss_for_dataset_in_fallback() -> None:
    result = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="fallback",
        metadata={"fallback_type": "UNKNOWN"},
    )
    CoverageRecoveryMetricsService.record_outcome("¿Qué datos tienes?", result)
    snapshot = CoverageRecoveryMetricsService.snapshot()
    assert snapshot["coverage_recovery_hits"] == 0
    assert snapshot["coverage_recovery_misses"] == 1


def test_record_hit_for_capability_discovery() -> None:
    result = HybridChatResult(
        handled_by="capability_discovery",
        success=True,
        answer="capabilities",
        metadata={"query_type": "capability_discovery"},
    )
    CoverageRecoveryMetricsService.record_outcome("¿Qué puedes hacer?", result)
    assert CoverageRecoveryMetricsService.snapshot()["coverage_recovery_hits"] == 1


def test_health_rejects_broken_planner(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.query_engine.business_query import BusinessQuery
    from app.query_engine.query_types import BusinessQueryType

    class BrokenPlanner:
        def plan(self, intent):  # noqa: ARG002
            return BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED)

    with pytest.raises(CoverageRecoveryHealthError, match="cobertura no planificada"):
        validate_coverage_recovery_health(planner=BrokenPlanner())
