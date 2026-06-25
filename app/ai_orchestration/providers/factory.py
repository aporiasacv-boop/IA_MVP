from app.ai_orchestration.constants import (
    PROVIDER_CLAUDE,
    PROVIDER_MOCK,
    PROVIDER_OLLAMA,
    PROVIDER_OPENAI,
    SUPPORTED_PROVIDERS,
)
from app.ai_orchestration.providers.base import BaseLLMProvider
from app.ai_orchestration.providers.claude_provider import ClaudeProvider
from app.ai_orchestration.providers.mock_provider import MockProvider
from app.ai_orchestration.providers.ollama_provider import OllamaProvider
from app.ai_orchestration.providers.openai_provider import OpenAIProvider
from app.core.settings import settings


def create_llm_provider(provider_name: str | None = None) -> BaseLLMProvider:
    name = (provider_name or settings.LLM_PROVIDER).strip().lower()
    if name not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Proveedor LLM desconocido: {name}")
    if name == PROVIDER_OPENAI:
        return OpenAIProvider()
    if name == PROVIDER_CLAUDE:
        return ClaudeProvider()
    if name == PROVIDER_OLLAMA:
        return OllamaProvider()
    return MockProvider()


def create_llm_provider_with_fallback() -> BaseLLMProvider:
    primary = create_llm_provider(settings.LLM_PROVIDER)
    fallback_name = (settings.LLM_FALLBACK_PROVIDER or "").strip().lower()
    if not fallback_name or fallback_name == settings.LLM_PROVIDER.lower():
        return _FallbackProvider(primary, None)
    try:
        fallback = create_llm_provider(fallback_name)
    except ValueError:
        fallback = None
    return _FallbackProvider(primary, fallback)


class _FallbackProvider(BaseLLMProvider):
    def __init__(self, primary: BaseLLMProvider, fallback: BaseLLMProvider | None) -> None:
        self._primary = primary
        self._fallback = fallback
        self._last_used = primary

    def generate_response(self, prompt: str):
        from app.ai_orchestration.metrics import LLMOrchestrationMetrics

        try:
            result = self._primary.generate_response(prompt)
            self._last_used = self._primary
            return result
        except Exception:
            if self._fallback is None:
                raise
            LLMOrchestrationMetrics.record_fallback(
                from_provider=self._primary.provider_name(),
                to_provider=self._fallback.provider_name(),
            )
            result = self._fallback.generate_response(prompt)
            self._last_used = self._fallback
            return result

    def health(self) -> dict:
        primary = self._primary.health()
        if primary.get("status") == "healthy":
            return primary
        if self._fallback is not None:
            return self._fallback.health()
        return primary

    def estimated_cost(self, tokens_input: int, tokens_output: int) -> float:
        return self._last_used.estimated_cost(tokens_input, tokens_output)

    def estimated_tokens(self, text: str) -> int:
        return self._last_used.estimated_tokens(text)

    def provider_name(self) -> str:
        return self._last_used.provider_name()

    @property
    def model_name(self) -> str:
        return self._last_used.model_name
