import pytest

from app.ai_orchestration.health import OrchestrationHealthError, validate_orchestration_health
from app.ai_orchestration.metrics import LLMOrchestrationMetrics


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    LLMOrchestrationMetrics.reset_for_tests()


def test_health_ok() -> None:
    result = validate_orchestration_health(
        {
            "provider_down": [],
            "timeout": [],
            "empty_response": [],
            "no_evidence": [],
            "negative_cost": [],
            "unknown_model": [],
        }
    )
    assert result["status"] == "healthy"


def test_health_provider_down() -> None:
    with pytest.raises(OrchestrationHealthError, match="caído"):
        validate_orchestration_health({"provider_down": [{"provider": "openai"}]})


def test_health_timeout() -> None:
    with pytest.raises(OrchestrationHealthError, match="Timeout"):
        validate_orchestration_health({"timeout": [{"provider": "openai"}]})


def test_health_empty_response() -> None:
    with pytest.raises(OrchestrationHealthError, match="vacías"):
        validate_orchestration_health({"empty_response": [{"provider": "mock"}]})


def test_health_negative_cost() -> None:
    with pytest.raises(OrchestrationHealthError, match="negativos"):
        validate_orchestration_health({"negative_cost": [{"cost": -1}]})
