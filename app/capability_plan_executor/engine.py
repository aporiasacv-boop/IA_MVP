import time
from typing import Any

from app.capability_plan_executor.constants import (
    COVERAGE_FULL_THRESHOLD,
    COVERAGE_PARTIAL_THRESHOLD,
    STRATEGY_FALLBACK,
    STRATEGY_MULTI,
    STRATEGY_SINGLE,
)
from app.capability_plan_executor.metrics import record_plan_execution
from app.capability_plan_executor.schemas import (
    CapabilityQueryRunner,
    EnrichedReasonerPlan,
    PlanExecutionOutcome,
)
from app.core.settings import settings
from app.schemas.hybrid_chat import HybridChatResult


class CapabilityPlanExecutor:
    """Ejecuta el plan del Capability Reasoner cuando hay cobertura suficiente."""

    def __init__(
        self,
        *,
        execute_capability: CapabilityQueryRunner,
        enabled: bool | None = None,
    ) -> None:
        self._execute_capability = execute_capability
        self._enabled = settings.CAPABILITY_PLAN_EXECUTOR_ENABLED if enabled is None else enabled

    def try_execute(
        self,
        *,
        question: str,
        session_id: str | None,
        result: HybridChatResult,
    ) -> HybridChatResult:
        if not self._enabled:
            return result

        if result.handled_by != "guided_fallback":
            return result

        started = time.perf_counter()
        plan = _parse_reasoner_plan(result.metadata)
        enriched_plan = _enrich_plan(plan)
        outcome = _resolve_outcome(enriched_plan)

        if outcome.execution_strategy == STRATEGY_FALLBACK or not enriched_plan.primary_capability:
            metadata = {
                **result.metadata,
                **_plan_payload(enriched_plan, result.metadata),
                **outcome.observability_metadata(),
            }
            record_plan_execution(
                executed=False,
                fallback_avoided=False,
                partial_execution=False,
            )
            return HybridChatResult(
                handled_by=result.handled_by,
                success=result.success,
                answer=result.answer,
                suggestions=result.suggestions,
                metadata=metadata,
            )

        executed = self._execute_capability(enriched_plan.primary_capability, session_id)
        execution_ms = (time.perf_counter() - started) * 1000
        outcome = outcome.model_copy(
            update={
                "plan_executed": True,
                "fallback_avoided": True,
                "execution_time_ms": execution_ms,
            }
        )

        record_plan_execution(
            executed=True,
            fallback_avoided=True,
            partial_execution=outcome.partial_execution,
        )

        merged_metadata = {
            **executed.metadata,
            **result.metadata,
            **_plan_payload(enriched_plan, result.metadata),
            **outcome.observability_metadata(),
            "plan_executor_source_question": question,
            "plan_executor_original_fallback_type": result.metadata.get("fallback_type"),
            "plan_executor_replaced_fallback": True,
        }

        return HybridChatResult(
            handled_by=executed.handled_by,
            success=executed.success,
            answer=executed.answer,
            suggestions=executed.suggestions or result.suggestions,
            metadata=merged_metadata,
        )


def _parse_reasoner_plan(metadata: dict[str, Any]) -> EnrichedReasonerPlan:
    raw = metadata.get("capability_reasoner_plan")
    if isinstance(raw, dict):
        return EnrichedReasonerPlan(
            reasoning_goal=str(raw.get("reasoning_goal", "")),
            selected_capabilities=list(raw.get("selected_capabilities", [])),
            estimated_coverage=float(raw.get("estimated_coverage", metadata.get("estimated_coverage", 0))),
            fallback_recommended=bool(raw.get("fallback_recommended", metadata.get("fallback_recommended", True))),
        )

    return EnrichedReasonerPlan(
        reasoning_goal=str(metadata.get("reasoning_goal", "")),
        selected_capabilities=list(metadata.get("selected_capabilities", [])),
        estimated_coverage=float(metadata.get("estimated_coverage", 0)),
        fallback_recommended=bool(metadata.get("fallback_recommended", True)),
    )


def _enrich_plan(plan: EnrichedReasonerPlan) -> EnrichedReasonerPlan:
    primary = plan.selected_capabilities[0] if plan.selected_capabilities else None
    strategy = _resolve_strategy(plan)
    return plan.model_copy(
        update={
            "execution_strategy": strategy,
            "primary_capability": primary,
        }
    )


def _resolve_strategy(plan: EnrichedReasonerPlan) -> str:
    coverage = plan.estimated_coverage
    if coverage < COVERAGE_PARTIAL_THRESHOLD or not plan.selected_capabilities:
        return STRATEGY_FALLBACK
    if coverage >= COVERAGE_FULL_THRESHOLD and len(plan.selected_capabilities) > 1:
        return STRATEGY_MULTI
    if coverage >= COVERAGE_PARTIAL_THRESHOLD:
        return STRATEGY_SINGLE
    return STRATEGY_FALLBACK


def _resolve_outcome(plan: EnrichedReasonerPlan) -> PlanExecutionOutcome:
    partial = (
        COVERAGE_PARTIAL_THRESHOLD <= plan.estimated_coverage < COVERAGE_FULL_THRESHOLD
        and plan.execution_strategy != STRATEGY_FALLBACK
    )
    return PlanExecutionOutcome(
        plan_executed=False,
        execution_strategy=plan.execution_strategy,
        primary_capability=plan.primary_capability,
        coverage_used=plan.estimated_coverage,
        partial_execution=partial,
        fallback_avoided=False,
        execution_time_ms=0.0,
    )


def _plan_payload(plan: EnrichedReasonerPlan, metadata: dict[str, Any]) -> dict[str, Any]:
    raw = metadata.get("capability_reasoner_plan")
    payload = dict(raw) if isinstance(raw, dict) else {}
    payload.update(
        {
            "reasoning_goal": plan.reasoning_goal,
            "selected_capabilities": plan.selected_capabilities,
            "estimated_coverage": plan.estimated_coverage,
            "fallback_recommended": plan.fallback_recommended,
            "execution_strategy": plan.execution_strategy,
            "primary_capability": plan.primary_capability,
        }
    )
    return {
        "execution_strategy": plan.execution_strategy,
        "primary_capability": plan.primary_capability,
        "capability_reasoner_plan": payload,
    }
