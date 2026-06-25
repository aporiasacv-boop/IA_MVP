import httpx

from app.ai_orchestration.constants import PROVIDER_OPENAI
from app.ai_orchestration.providers.base import BaseLLMProvider
from app.ai_orchestration.schemas import LLMGenerateResult
from app.core.settings import settings


class OpenAIProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.api_key = api_key or settings.OPENAI_API_KEY
        self._model = model or settings.OPENAI_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

    def generate_response(self, prompt: str) -> LLMGenerateResult:
        if not self.api_key:
            raise ConnectionError("OPENAI_API_KEY no configurada")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un analista ejecutivo empresarial. Responde ÚNICAMENTE con "
                        "información del paquete de evidencia. Si no hay evidencia suficiente, "
                        "indícalo explícitamente. Usa las secciones RESUMEN EJECUTIVO y ANÁLISIS DETALLADO."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        try:
            with httpx.Client(timeout=httpx.Timeout(self.timeout, connect=5.0)) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.TimeoutException as exc:
            raise TimeoutError("Timeout al contactar OpenAI") from exc
        except httpx.HTTPError as exc:
            raise ConnectionError(f"Error HTTP OpenAI: {exc}") from exc

        choices = body.get("choices") or []
        if not choices:
            raise ValueError("Respuesta vacía de OpenAI")
        text = str(choices[0].get("message", {}).get("content", "")).strip()
        if not text:
            raise ValueError("Respuesta vacía de OpenAI")
        usage = body.get("usage") or {}
        tokens_in = int(usage.get("prompt_tokens") or self.estimated_tokens(prompt))
        tokens_out = int(usage.get("completion_tokens") or self.estimated_tokens(text))
        return LLMGenerateResult(
            text=text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            model=self._model,
            provider=self.provider_name(),
        )

    def health(self) -> dict:
        healthy = bool(self.api_key) and bool(self._model)
        return {
            "status": "healthy" if healthy else "unhealthy",
            "provider": self.provider_name(),
            "model": self._model,
        }

    def estimated_cost(self, tokens_input: int, tokens_output: int) -> float:
        input_cost = settings.GPT_COST_PER_1K_INPUT_TOKENS
        output_cost = settings.GPT_COST_PER_1K_OUTPUT_TOKENS
        if input_cost <= 0 and output_cost <= 0:
            fallback = settings.GPT_COST_PER_1K_TOKENS
            total = tokens_input + tokens_output
            if total <= 0 or fallback <= 0:
                return 0.0
            return round((total / 1000.0) * fallback, 6)
        cost = (tokens_input / 1000.0) * input_cost + (tokens_output / 1000.0) * output_cost
        return round(cost, 6)

    def estimated_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def provider_name(self) -> str:
        return PROVIDER_OPENAI

    @property
    def model_name(self) -> str:
        return self._model
