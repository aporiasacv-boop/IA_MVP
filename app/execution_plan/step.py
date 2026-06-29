from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionStep:
    """Un paso del plan: referencia a una Capability o etapa de enrutamiento."""

    step_id: str
