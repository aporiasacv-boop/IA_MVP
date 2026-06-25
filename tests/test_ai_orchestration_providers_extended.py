from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.ai_orchestration.executive_response_engine import _parse_sections, _extract_citations
from app.ai_orchestration.metrics import LLMOrchestrationMetrics
from app.ai_orchestration.providers.claude_provider import ClaudeProvider
from app.ai_orchestration.providers.factory import _FallbackProvider, create_llm_provider
from app.ai_orchestration.providers.mock_provider import MockProvider
from app.ai_orchestration.providers.ollama_provider import OllamaProvider
from app.ai_orchestration.providers.openai_provider import OpenAIProvider
from app.ai_orchestration.service import AIOrchestrationService
from app.evidence_package.example_data import build_example_package


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    LLMOrchestrationMetrics.reset_for_tests()


def test_parse_sections_structured() -> None:
    text = "RESUMEN EJECUTIVO:\nResumen aquí.\n\nANÁLISIS DETALLADO:\nAnálisis aquí."
    summary, analysis = _parse_sections(text)
    assert "Resumen" in summary
    assert "Análisis" in analysis


def test_extract_citations() -> None:
    package = build_example_package()
    citations = _extract_citations(package, "total_movements WALMART")
    assert isinstance(citations, list)


def test_openai_provider_generate() -> None:
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini")
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "RESUMEN EJECUTIVO:\nOk\n\nANÁLISIS DETALLADO:\nOk"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }
    with patch("httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_response
        result = provider.generate_response("prompt")
    assert result.tokens_input == 10


def test_claude_provider_generate() -> None:
    provider = ClaudeProvider(api_key="sk-test", model="claude-3-5-sonnet-20241022")
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "content": [{"type": "text", "text": "RESUMEN EJECUTIVO:\nOk\n\nANÁLISIS DETALLADO:\nOk"}],
        "usage": {"input_tokens": 12, "output_tokens": 6},
    }
    with patch("httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_response
        result = provider.generate_response("prompt")
    assert result.provider == "claude"


def test_ollama_provider_generate() -> None:
    provider = OllamaProvider(base_url="http://localhost:11434", model="test")
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "response": "RESUMEN EJECUTIVO:\nOk\n\nANÁLISIS DETALLADO:\nOk",
        "prompt_eval_count": 8,
        "eval_count": 4,
    }
    with patch("httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_response
        result = provider.generate_response("prompt")
    assert result.tokens_output == 4


def test_ollama_provider_health() -> None:
    provider = OllamaProvider()
    with patch("httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.get.return_value.status_code = 200
        assert provider.health()["status"] == "healthy"


def test_fallback_provider_on_failure() -> None:
    primary = MagicMock()
    primary.provider_name.return_value = "openai"
    primary.generate_response.side_effect = RuntimeError("down")
    fallback = MockProvider()
    provider = _FallbackProvider(primary, fallback)
    result = provider.generate_response("test")
    assert result.provider == "mock"
    assert LLMOrchestrationMetrics.llm_fallbacks == 1


def test_service_generate_from_package() -> None:
    from app.ai_orchestration.executive_response_engine import ExecutiveResponseEngine

    service = AIOrchestrationService(MagicMock(), ExecutiveResponseEngine(MockProvider()))
    package = build_example_package()
    response = service.generate_from_package(package)
    assert response.executive_summary


def test_openai_no_api_key() -> None:
    provider = OpenAIProvider(api_key="", model="gpt-4o-mini")
    with pytest.raises(ConnectionError):
        provider.generate_response("x")


def test_claude_estimated_cost_with_rates() -> None:
    provider = ClaudeProvider(api_key="k", model="claude-3-5-sonnet-20241022")
    assert provider.estimated_cost(1000, 500) >= 0


def test_create_each_provider() -> None:
    from app.ai_orchestration.constants import PROVIDER_CLAUDE, PROVIDER_OLLAMA, PROVIDER_OPENAI

    assert create_llm_provider(PROVIDER_OPENAI).__class__.__name__ == "OpenAIProvider"
    assert create_llm_provider(PROVIDER_CLAUDE).__class__.__name__ == "ClaudeProvider"
    assert create_llm_provider(PROVIDER_OLLAMA).__class__.__name__ == "OllamaProvider"


def test_openai_http_error() -> None:
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini")
    with patch("httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.side_effect = httpx.HTTPError("fail")
        with pytest.raises(ConnectionError):
            provider.generate_response("prompt")


def test_openai_empty_choices() -> None:
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini")
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"choices": []}
    with patch("httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_response
        with pytest.raises(ValueError, match="vacía"):
            provider.generate_response("prompt")


def test_ollama_empty_response() -> None:
    provider = OllamaProvider(base_url="http://localhost:11434", model="test")
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"response": ""}
    with patch("httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_response
        with pytest.raises(ValueError, match="vacía"):
            provider.generate_response("prompt")


def test_fallback_provider_health_uses_fallback() -> None:
    primary = MagicMock()
    primary.health.return_value = {"status": "unhealthy"}
    fallback = MockProvider()
    provider = _FallbackProvider(primary, fallback)
    assert provider.health()["status"] == "healthy"
