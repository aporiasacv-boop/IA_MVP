from __future__ import annotations

from dataclasses import dataclass

from app.execution_plan.constants import BUSINESS_PIPELINE, INSTITUTIONAL_KNOWLEDGE
from app.execution_plan.step import ExecutionStep


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """Secuencia ordenada de pasos que describe qué ejecutar en una consulta."""

    steps: tuple[ExecutionStep, ...]

    @classmethod
    def default_inquiry(cls) -> ExecutionPlan:
        """Plan estático equivalente al flujo actual de consulta híbrida."""
        return cls(
            steps=(
                ExecutionStep(step_id=INSTITUTIONAL_KNOWLEDGE),
                ExecutionStep(step_id=BUSINESS_PIPELINE),
            )
        )
