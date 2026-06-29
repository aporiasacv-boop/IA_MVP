import pytest

from app.capability_reasoning_audit.engine import CapabilityReasoningAudit
from app.capability_reasoning_audit.metrics import audit_metrics_snapshot, reset_audit_metrics_for_tests
from app.conversation_ux.constants import GATEWAY_DECISION_CONVERSATION
from app.conversation_ux.gateway import GatewayRouteOutcome
from app.reasoning_engine.constants import ROUTE_BUSINESS_PIPELINE
from app.reasoning_engine.fallback import rule_based_decision
from app.reasoning_engine.governor import GovernanceOutcome
from app.reasoning_engine.schemas import ReasoningDecision
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    reset_audit_metrics_for_tests()


@pytest.fixture
def audit_engine() -> CapabilityReasoningAudit:
    return CapabilityReasoningAudit(enabled=True)


def _gateway_outcome() -> GatewayRouteOutcome:
    return GatewayRouteOutcome(
        decision=GATEWAY_DECISION_CONVERSATION,
        reason="test",
        time_ms=0.0,
    )


def _governance() -> GovernanceOutcome:
    return GovernanceOutcome(
        governed=False,
        route=None,
        rule="none",
        reason="test",
        confidence=0.5,
        time_ms=0.0,
        pipeline_skipped=False,
    )


def test_audit_does_not_change_answer_or_handled_by(audit_engine: CapabilityReasoningAudit) -> None:
    original = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Respuesta original sin cambios.",
        metadata={
            "query_type": "UNSUPPORTED",
            "fallback_type": "UNSUPPORTED_CAPABILITY",
            "reasoning_intent": "business_query",
            "reasoning_confidence": 0.82,
            "reasoning_explanation": "Consulta empresarial ambigua.",
            "reasoning_actual_route": "clarification",
        },
    )
    decision = rule_based_decision("Analiza el universo de clientes")

    audited = audit_engine.observe(
        question="Analiza el universo de clientes",
        reasoning_decision=decision,
        result=original,
        gateway_outcome=_gateway_outcome(),
        governance=_governance(),
    )

    assert audited.handled_by == original.handled_by
    assert audited.answer == original.answer
    assert audited.success == original.success


def test_audit_flags_reusable_capabilities_on_fallback(audit_engine: CapabilityReasoningAudit) -> None:
    result = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="No pude resolver la consulta.",
        metadata={
            "fallback_type": "UNSUPPORTED_CAPABILITY",
            "reasoning_intent": "business_query",
            "reasoning_confidence": 0.84,
            "reasoning_explanation": "Consulta analítica sobre clientes.",
            "reasoning_actual_route": "clarification",
        },
    )

    audited = audit_engine.observe(
        question="Analiza el universo de clientes",
        reasoning_decision=ReasoningDecision(
            intent="customer_analysis",
            confidence=0.84,
            recommended_route=ROUTE_BUSINESS_PIPELINE,
            explanation="Consulta analítica sobre clientes.",
        ),
        result=result,
        gateway_outcome=_gateway_outcome(),
        governance=_governance(),
    )

    metadata = audited.metadata
    assert metadata["audit_selected_capability"] == "NONE"
    assert metadata["audit_final_route"] == "clarification"
    assert metadata["audit_capability_count"] == 10
    assert "audit_reasoning_ms" in metadata

    audit_payload = metadata["capability_reasoning_audit"]
    assert audit_payload["evaluation"]["classification"] == "Incorrecto"
    assert audit_payload["evaluation"]["reusable_capabilities_exist"] is True
    assert "TOP_CLIENTES" in audit_payload["report_text"]
    assert "KPIS" in audit_payload["report_text"]
    assert audit_metrics_snapshot()["fallback_with_reusable"] == 1


def test_audit_marks_pipeline_selection_as_correct(audit_engine: CapabilityReasoningAudit) -> None:
    result = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Los cinco clientes principales concentran la actividad.",
        metadata={
            "query_type": "TOP_CLIENTES",
            "reasoning_intent": "business_query",
            "reasoning_confidence": 0.9,
            "reasoning_explanation": "Ranking de clientes.",
            "reasoning_actual_route": ROUTE_BUSINESS_PIPELINE,
        },
    )

    audited = audit_engine.observe(
        question="Muéstrame los principales clientes",
        reasoning_decision=rule_based_decision("Muéstrame los principales clientes"),
        result=result,
        gateway_outcome=GatewayRouteOutcome(decision="business", reason="pipeline", time_ms=0.0),
        governance=_governance(),
    )

    audit_payload = audited.metadata["capability_reasoning_audit"]
    assert audit_payload["decision"]["selected_capability"] == "TOP_CLIENTES"
    assert audit_payload["evaluation"]["classification"] == "Correcto"
    assert audited.metadata["audit_selected_capability"] == "TOP_CLIENTES"


def test_audit_disabled_returns_original_result() -> None:
    engine = CapabilityReasoningAudit(enabled=False)
    original = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="50 clientes.",
        metadata={"query_type": "COUNT_CLIENTES"},
    )
    audited = engine.observe(
        question="¿Cuántos clientes existen?",
        reasoning_decision=None,
        result=original,
        gateway_outcome=_gateway_outcome(),
        governance=_governance(),
    )
    assert audited.metadata == original.metadata
