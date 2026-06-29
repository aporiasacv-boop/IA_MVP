from app.capability_executor.executor import CapabilityExecutor
from app.execution_plan.plan import ExecutionPlan
from app.schemas.hybrid_chat import HybridChatResult


class EnterpriseRuntime:
    """Coordinador de consultas empresariales.

    Sprint 6: recorre el plan y delega la ejecución al Capability Executor.
    """

    def __init__(
        self,
        execution_plan: ExecutionPlan,
        capability_executor: CapabilityExecutor,
    ) -> None:
        self._execution_plan = execution_plan
        self._capability_executor = capability_executor

    def process_inquiry(
        self,
        message: str,
        session_id: str | None = None,
    ) -> HybridChatResult:
        for step in self._execution_plan.steps:
            result = self._capability_executor.execute(step, message, session_id)
            if result is not None:
                return result
        raise RuntimeError("El plan de ejecución no produjo un resultado")
