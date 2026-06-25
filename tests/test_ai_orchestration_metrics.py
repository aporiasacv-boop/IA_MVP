import pytest

from app.ai_orchestration.health import OrchestrationHealthError, validate_orchestration_health
from app.ai_orchestration.metrics import LLMOrchestrationMetrics


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    LLMOrchestrationMetrics.reset_for_tests()


def test_health_no_evidence() -> None:
    with pytest.raises(OrchestrationHealthError, match="evidencia"):
        validate_orchestration_health({"no_evidence": [{"package_id": "x"}]})


def test_health_unknown_model() -> None:
    with pytest.raises(OrchestrationHealthError, match="desconocido"):
        validate_orchestration_health({"unknown_model": [{"model": "x"}]})


def test_metrics_record_with_user() -> None:
    LLMOrchestrationMetrics.record_request(
        provider="mock",
        model="m",
        tokens_input=10,
        tokens_output=5,
        estimated_cost=0.001,
        response_time=0.2,
        hallucination_guard=True,
        user_id="user1",
    )
    assert LLMOrchestrationMetrics.user_cost["user1"] > 0
    assert LLMOrchestrationMetrics.hallucination_guard_triggered == 1


def test_metrics_record_fallback_and_events() -> None:
    LLMOrchestrationMetrics.record_fallback(from_provider="openai", to_provider="mock")
    LLMOrchestrationMetrics.record_timeout("openai")
    LLMOrchestrationMetrics.record_empty_response("mock")
    LLMOrchestrationMetrics.record_no_evidence("pkg1")
    LLMOrchestrationMetrics.record_unknown_model("unknown")
    issues = LLMOrchestrationMetrics.health_issues()
    assert issues["timeout"]
