from app.ai_orchestration.constants import PROVIDER_MOCK
from app.ai_orchestration.providers.base import BaseLLMProvider
from app.ai_orchestration.schemas import LLMGenerateResult
from app.core.settings import settings


class MockProvider(BaseLLMProvider):
    def __init__(self, model: str | None = None) -> None:
        self._model = model or "mock-executive-v1"

    def generate_response(self, prompt: str) -> LLMGenerateResult:
        tokens_in = self.estimated_tokens(prompt)
        summary = (
            "Resumen ejecutivo basado exclusivamente en la evidencia proporcionada. "
            "Los hallazgos y recomendaciones reflejan el paquete de evidencia empresarial."
        )
        analysis = (
            "Análisis detallado: la respuesta se limita a los hechos, señales, riesgos "
            "y recomendaciones incluidos en el paquete. No se ha consultado SQL ni fuentes externas."
        )
        text = f"RESUMEN EJECUTIVO:\n{summary}\n\nANÁLISIS DETALLADO:\n{analysis}"
        tokens_out = self.estimated_tokens(text)
        return LLMGenerateResult(
            text=text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            model=self._model,
            provider=self.provider_name(),
        )

    def health(self) -> dict:
        return {"status": "healthy", "provider": self.provider_name(), "model": self._model}

    def estimated_cost(self, tokens_input: int, tokens_output: int) -> float:
        return 0.0

    def estimated_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def provider_name(self) -> str:
        return PROVIDER_MOCK

    @property
    def model_name(self) -> str:
        return self._model
