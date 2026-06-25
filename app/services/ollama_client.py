import httpx

from app.core.settings import settings


class OllamaError(Exception):
    pass


class OllamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        try:
            timeout = httpx.Timeout(self.timeout, connect=3.0)
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.TimeoutException as exc:
            raise OllamaError("Tiempo de espera agotado al contactar Ollama") from exc
        except httpx.HTTPError as exc:
            raise OllamaError(f"Error HTTP al contactar Ollama: {exc}") from exc
        except ValueError as exc:
            raise OllamaError("Respuesta invalida de Ollama") from exc

        text = body.get("response", "").strip()
        if not text:
            raise OllamaError("Ollama devolvio una respuesta vacia")
        return text

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except httpx.HTTPError:
            return False
