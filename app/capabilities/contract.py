from typing import Protocol

from app.schemas.hybrid_chat import HybridChatResult


class Capability(Protocol):
    """Contrato mínimo de ejecución para todas las Capabilities del sistema."""

    def execute(
        self,
        message: str,
        session_id: str | None = None,
    ) -> HybridChatResult | None:
        """Ejecuta la capability sobre una consulta y devuelve resultado o None."""
        ...
