from abc import ABC, abstractmethod

from app.ai_orchestration.schemas import LLMGenerateResult


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> LLMGenerateResult:
        """Genera respuesta a partir del prompt construido desde EEP."""

    @abstractmethod
    def health(self) -> dict:
        """Estado del proveedor."""

    @abstractmethod
    def estimated_cost(self, tokens_input: int, tokens_output: int) -> float:
        """Costo estimado en USD para los tokens indicados."""

    @abstractmethod
    def estimated_tokens(self, text: str) -> int:
        """Estimación de tokens para un texto."""

    @abstractmethod
    def provider_name(self) -> str:
        """Identificador del proveedor."""

    @property
    def model_name(self) -> str:
        return ""
