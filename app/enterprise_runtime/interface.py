from typing import Protocol

from app.schemas.hybrid_chat import HybridChatResult


class EnterpriseRuntimeInterface(Protocol):
    """Interfaz pública del Enterprise Runtime — punto de coordinación de consultas."""

    def process_inquiry(
        self,
        message: str,
        session_id: str | None = None,
    ) -> HybridChatResult:
        """Procesa una consulta empresarial y devuelve el resultado unificado."""
        ...
