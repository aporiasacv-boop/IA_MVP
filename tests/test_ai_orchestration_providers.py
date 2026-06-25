import pytest

from app.ai_orchestration.constants import PROVIDER_MOCK, PROVIDER_OPENAI
from app.ai_orchestration.metrics import LLMOrchestrationMetrics
from app.ai_orchestration.providers.factory import create_llm_provider, create_llm_provider_with_fallback
from app.ai_orchestration.providers.mock_provider import MockProvider
from app.ai_orchestration.providers.openai_provider import OpenAIProvider


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    LLMOrchestrationMetrics.reset_for_tests()


def test_create_mock_provider() -> None:
    provider = create_llm_provider(PROVIDER_MOCK)
    assert isinstance(provider, MockProvider)
    assert provider.provider_name() == PROVIDER_MOCK


def test_mock_provider_generate() -> None:
    provider = MockProvider()
    result = provider.generate_response("test prompt")
    assert "RESUMEN EJECUTIVO" in result.text
    assert result.tokens_input > 0


def test_mock_provider_health() -> None:
    assert MockProvider().health()["status"] == "healthy"


def test_openai_provider_cost() -> None:
    provider = OpenAIProvider(api_key="test", model="gpt-4o-mini")
    assert provider.estimated_cost(1000, 500) >= 0


def test_unknown_provider_raises() -> None:
    with pytest.raises(ValueError, match="desconocido"):
        create_llm_provider("unknown")


def test_fallback_provider_uses_primary() -> None:
    provider = create_llm_provider_with_fallback()
    result = provider.generate_response("hola")
    assert result.text


def test_metrics_record_request() -> None:
    LLMOrchestrationMetrics.record_request(
        provider="mock",
        model="m",
        tokens_input=100,
        tokens_output=50,
        estimated_cost=0.01,
        response_time=0.5,
        hallucination_guard=False,
    )
    snap = LLMOrchestrationMetrics.snapshot()
    assert snap["llm_requests"] == 1
    assert snap["tokens_input"] == 100
