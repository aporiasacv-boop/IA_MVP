import time

from app.capability_reasoner.metrics import record_reasoner_metrics
from app.capability_reasoner.planner import build_reasoner_plan
from app.capability_reasoner.scoring import infer_reasoning_goal, score_registered_capabilities
from app.core.settings import settings
from app.reasoning_engine.schemas import ReasoningDecision
from app.schemas.hybrid_chat import HybridChatResult


class CapabilityReasoner:
    """Construye un plan razonado sobre capabilities existentes. No ejecuta ni responde."""

    def __init__(self, *, enabled: bool | None = None) -> None:
        self._enabled = settings.CAPABILITY_REASONER_ENABLED if enabled is None else enabled

    def recommend(
        self,
        *,
        question: str,
        reasoning_decision: ReasoningDecision | None,
        metadata: dict | None = None,
    ) -> tuple[HybridChatResult | None, dict]:
        """Retorna metadata de observabilidad. Si se pasa result, lo devuelve enriquecido sin cambiar answer."""
        if not self._enabled:
            return None, {}

        started = time.perf_counter()
        safe_metadata = metadata or {}
        intent = _read_str(safe_metadata.get("reasoning_intent")) or (
            reasoning_decision.intent if reasoning_decision else None
        )
        explanation = _read_str(safe_metadata.get("reasoning_explanation")) or (
            reasoning_decision.explanation if reasoning_decision else None
        )
        confidence = _read_float(safe_metadata.get("reasoning_confidence")) or (
            reasoning_decision.confidence if reasoning_decision else None
        )

        goal = infer_reasoning_goal(question, intent=intent, explanation=explanation)
        candidates = score_registered_capabilities(
            question,
            intent=intent,
            explanation=explanation,
            reasoning_confidence=confidence,
        )
        plan = build_reasoner_plan(reasoning_goal=goal, candidates=candidates)

        record_reasoner_metrics(
            fallback_recommended=plan.fallback_recommended,
            combination=len(plan.selected_capabilities) > 1,
        )

        observability = {
            **plan.observability_metadata(),
            "reasoner_plan_ms": round((time.perf_counter() - started) * 1000, 2),
        }
        return None, observability

    def enrich_result(
        self,
        *,
        question: str,
        reasoning_decision: ReasoningDecision | None,
        result: HybridChatResult,
    ) -> HybridChatResult:
        if not self._enabled:
            return result

        _, observability = self.recommend(
            question=question,
            reasoning_decision=reasoning_decision,
            metadata=result.metadata,
        )
        if not observability:
            return result

        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={**result.metadata, **observability},
        )


def _read_str(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _read_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None
