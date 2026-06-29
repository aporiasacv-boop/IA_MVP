import time

from app.core.settings import settings
from app.enterprise_evidence_planner.metrics import record_evidence_plan
from app.enterprise_evidence_planner.planner import build_evidence_plan
from app.reasoning_engine.schemas import ReasoningDecision
from app.schemas.hybrid_chat import HybridChatResult


class EnterpriseEvidencePlanner:
    """Transforma intención empresarial en plan de evidencia. No ejecuta ni responde."""

    def __init__(self, *, enabled: bool | None = None) -> None:
        self._enabled = (
            settings.ENTERPRISE_EVIDENCE_PLANNER_ENABLED if enabled is None else enabled
        )

    def enrich_result(
        self,
        *,
        question: str,
        reasoning_decision: ReasoningDecision | None,
        result: HybridChatResult,
    ) -> HybridChatResult:
        if not self._enabled:
            return result

        started = time.perf_counter()
        metadata = result.metadata
        intent = _read_str(metadata.get("reasoning_intent")) or (
            reasoning_decision.intent if reasoning_decision else None
        )
        explanation = _read_str(metadata.get("reasoning_explanation")) or (
            reasoning_decision.explanation if reasoning_decision else None
        )

        plan = build_evidence_plan(question=question, intent=intent, explanation=explanation)
        planning_ms = (time.perf_counter() - started) * 1000
        record_evidence_plan(evidence_count=len(plan.required_evidence))

        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={**metadata, **plan.observability_metadata(planning_ms)},
        )


def _read_str(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None
