from collections.abc import Callable

from pydantic import BaseModel, Field

from app.schemas.hybrid_chat import HybridChatResult

CapabilityQueryRunner = Callable[[str, str | None], HybridChatResult]


class EnrichedReasonerPlan(BaseModel):
    reasoning_goal: str = ""
    selected_capabilities: list[str] = Field(default_factory=list)
    estimated_coverage: float = 0.0
    fallback_recommended: bool = True
    execution_strategy: str = "FALLBACK"
    primary_capability: str | None = None


class PlanExecutionOutcome(BaseModel):
    plan_executed: bool = False
    execution_strategy: str = "FALLBACK"
    primary_capability: str | None = None
    coverage_used: float = 0.0
    partial_execution: bool = False
    fallback_avoided: bool = False
    execution_time_ms: float = 0.0

    def observability_metadata(self) -> dict:
        return {
            "plan_executed": self.plan_executed,
            "execution_strategy": self.execution_strategy,
            "primary_capability": self.primary_capability,
            "coverage_used": round(self.coverage_used, 2),
            "partial_execution": self.partial_execution,
            "fallback_avoided": self.fallback_avoided,
            "execution_time_ms": round(self.execution_time_ms, 2),
        }
