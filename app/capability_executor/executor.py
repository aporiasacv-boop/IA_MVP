from app.capability_registry.registry import CapabilityRegistry
from app.execution_plan.step import ExecutionStep
from app.schemas.hybrid_chat import HybridChatResult


class CapabilityExecutor:
    """Ejecuta un ExecutionStep invocando Capabilities del catálogo oficial."""

    def __init__(self, capability_registry: CapabilityRegistry) -> None:
        self._capability_registry = capability_registry

    def execute(
        self,
        step: ExecutionStep,
        message: str,
        session_id: str | None = None,
    ) -> HybridChatResult | None:
        capability = self._capability_registry.get(step.step_id)
        return capability.execute(message, session_id=session_id)
