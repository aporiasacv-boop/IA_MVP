import time

from app.capability_reasoning_audit.compatibility import (
    assess_query_type_compatibility,
    capability_label,
)
from app.capability_reasoning_audit.constants import AUDITABLE_QUERY_TYPES
from app.capability_reasoning_audit.evaluator import evaluate_capability_outcome
from app.capability_reasoning_audit.metrics import record_audit_metrics
from app.capability_reasoning_audit.reporter import build_report
from app.capability_reasoning_audit.schemas import AuditedCapability, CapabilityDecision
from app.conversation_ux.gateway import GatewayRouteOutcome
from app.core.settings import settings
from app.reasoning_engine.governor import GovernanceOutcome
from app.reasoning_engine.route_resolver import resolve_actual_route
from app.reasoning_engine.schemas import ReasoningDecision
from app.schemas.hybrid_chat import HybridChatResult


class CapabilityReasoningAudit:
    """Observa y explica decisiones de ruteo. Nunca modifica el flujo ni la respuesta."""

    def __init__(self, *, enabled: bool | None = None) -> None:
        self._enabled = (
            settings.CAPABILITY_REASONING_AUDIT_ENABLED if enabled is None else enabled
        )

    def observe(
        self,
        *,
        question: str,
        reasoning_decision: ReasoningDecision | None,
        result: HybridChatResult,
        gateway_outcome: GatewayRouteOutcome,
        governance: GovernanceOutcome,
    ) -> HybridChatResult:
        if not self._enabled:
            return result

        started = time.perf_counter()
        metadata = result.metadata
        intent = _read_str(metadata.get("reasoning_intent")) or (
            reasoning_decision.intent if reasoning_decision else None
        )
        confidence = _read_float(metadata.get("reasoning_confidence")) or (
            reasoning_decision.confidence if reasoning_decision else None
        )
        explanation = _read_str(metadata.get("reasoning_explanation")) or (
            reasoning_decision.explanation if reasoning_decision else None
        )

        capabilities = self._audit_capabilities(question, intent=intent)
        decision = self._build_decision(result, gateway_outcome, governance)
        evaluation = evaluate_capability_outcome(
            capabilities=capabilities,
            decision=decision,
            result=result,
        )
        report = build_report(
            question=question,
            intent=intent,
            confidence=confidence,
            explanation=explanation,
            capabilities=capabilities,
            decision=decision,
            evaluation=evaluation,
        )
        audit_ms = (time.perf_counter() - started) * 1000
        record_audit_metrics(
            fallback_with_reusable=decision.fallback_used and evaluation.reusable_capabilities_exist,
            incorrect=evaluation.classification == "Incorrecto",
        )

        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={
                **metadata,
                **report.observability_metadata(audit_ms),
            },
        )

    def _audit_capabilities(self, question: str, *, intent: str | None) -> list[AuditedCapability]:
        audited: list[AuditedCapability] = []
        for query_type in AUDITABLE_QUERY_TYPES:
            compatibility, rationale = assess_query_type_compatibility(
                question,
                query_type,
                intent=intent,
            )
            audited.append(
                AuditedCapability(
                    capability_id=query_type.value,
                    label=capability_label(query_type),
                    compatibility=compatibility,
                    rationale=rationale,
                )
            )
        return audited

    def _build_decision(
        self,
        result: HybridChatResult,
        gateway_outcome: GatewayRouteOutcome,
        governance: GovernanceOutcome,
    ) -> CapabilityDecision:
        metadata = result.metadata
        query_type = _read_str(metadata.get("query_type"))
        selected_capability = query_type.upper() if query_type else "NONE"
        final_route = _read_str(metadata.get("reasoning_actual_route")) or resolve_actual_route(
            result,
            gateway_outcome,
        )
        fallback_used = result.handled_by == "guided_fallback"
        fallback_type = _read_str(metadata.get("fallback_type"))
        reason = _decision_reason(
            result=result,
            governance=governance,
            gateway_outcome=gateway_outcome,
            fallback_used=fallback_used,
        )
        return CapabilityDecision(
            selected_capability=selected_capability,
            final_route=final_route,
            fallback_used=fallback_used,
            fallback_type=fallback_type,
            handled_by=result.handled_by,
            reason=reason,
        )


def _decision_reason(
    *,
    result: HybridChatResult,
    governance: GovernanceOutcome,
    gateway_outcome: GatewayRouteOutcome,
    fallback_used: bool,
) -> str:
    if fallback_used:
        fallback_type = result.metadata.get("fallback_type", "UNKNOWN")
        return f"Guided Fallback activado ({fallback_type})."
    if governance.governed:
        return f"Ruta gobernada: {governance.route} ({governance.reason})."
    if gateway_outcome.decision == "conversation":
        return f"Gateway conversacional: {gateway_outcome.reason}."
    if result.handled_by == "business_pipeline":
        query_type = result.metadata.get("query_type", "UNKNOWN")
        return f"Business Pipeline ejecutó query_type={query_type}."
    if result.handled_by == "conversation_memory":
        return "Memoria conversacional resolvió la consulta."
    if result.handled_by in {"business_knowledge", "product_identity"}:
        return "Conocimiento institucional respondió la consulta."
    return f"Ruta final por handled_by={result.handled_by}."


def _read_str(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _read_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None
