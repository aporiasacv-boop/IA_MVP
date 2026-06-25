import httpx

from app.ai_orchestration.constants import PROVIDER_OLLAMA
from app.ai_orchestration.providers.base import BaseLLMProvider
from app.ai_orchestration.schemas import LLMGenerateResult
from app.core.settings import settings


class OllamaProvider(BaseLLMProvider):
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

    def generate_response(self, prompt: str) -> LLMGenerateResult:
        url = f"{self.base_url}/api/generate"
        payload = {"model": self._model, "prompt": prompt, "stream": False}
        try:
            with httpx.Client(timeout=httpx.Timeout(self.timeout, connect=3.0)) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.TimeoutException as exc:
            raise TimeoutError("Timeout al contactar Ollama") from exc
        except httpx.HTTPError as exc:
            raise ConnectionError(f"Error HTTP Ollama: {exc}") from exc

        text = str(body.get("response", "")).strip()
        if not text:
            raise ValueError("Respuesta vacía de Ollama")
        tokens_in = int(body.get("prompt_eval_count") or self.estimated_tokens(prompt))
        tokens_out = int(body.get("eval_count") or self.estimated_tokens(text))
        return LLMGenerateResult(
            text=text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            model=self._model,
            provider=self.provider_name(),
        )

    def health(self) -> dict:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                healthy = response.status_code == 200
        except httpx.HTTPError:
            healthy = False
        return {
            "status": "healthy" if healthy else "unhealthy",
            "provider": self.provider_name(),
            "model": self._model,
        }

    def estimated_cost(self, tokens_input: int, tokens_output: int) -> float:
        total = tokens_input + tokens_output
        if total <= 0 or settings.OLLAMA_COST_PER_1K_TOKENS <= 0:
            return 0.0
        return round((total / 1000.0) * settings.OLLAMA_COST_PER_1K_TOKENS, 6)

    def estimated_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def provider_name(self) -> str:
        return PROVIDER_OLLAMA

    @property
    def model_name(self) -> str:
        return self._model
