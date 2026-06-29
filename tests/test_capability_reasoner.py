import pytest

from app.capability_reasoner.engine import CapabilityReasoner
from app.capability_reasoner.metrics import reasoner_metrics_snapshot, reset_reasoner_metrics_for_tests
from app.reasoning_engine.constants import ROUTE_BUSINESS_PIPELINE
from app.reasoning_engine.schemas import ReasoningDecision
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    reset_reasoner_metrics_for_tests()


@pytest.fixture
def reasoner() -> CapabilityReasoner:
    return CapabilityReasoner(enabled=True)


def test_reasoner_does_not_change_answer_or_handled_by(reasoner: CapabilityReasoner) -> None:
    original = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Respuesta sin cambios.",
        metadata={
            "reasoning_intent": "business_query",
            "reasoning_explanation": "Consulta analítica sobre clientes.",
            "reasoning_confidence": 0.84,
        },
    )

    enriched = reasoner.enrich_result(
        question="Analiza el universo de clientes",
        reasoning_decision=ReasoningDecision(
            intent="customer_analysis",
            confidence=0.84,
            recommended_route=ROUTE_BUSINESS_PIPELINE,
            explanation="Consulta analítica sobre clientes.",
        ),
        result=original,
    )

    assert enriched.handled_by == original.handled_by
    assert enriched.answer == original.answer


def test_reasoner_recommends_reuse_plan_for_client_analysis(reasoner: CapabilityReasoner) -> None:
    enriched = reasoner.enrich_result(
        question="Analiza el universo de clientes",
        reasoning_decision=ReasoningDecision(
            intent="customer_analysis",
            confidence=0.84,
            recommended_route=ROUTE_BUSINESS_PIPELINE,
            explanation="Consulta analítica sobre clientes.",
        ),
        result=HybridChatResult(
            handled_by="guided_fallback",
            success=True,
            answer="Fallback.",
            metadata={
                "reasoning_intent": "customer_analysis",
                "reasoning_confidence": 0.84,
                "reasoning_explanation": "Consulta analítica sobre clientes.",
            },
        ),
    )

    metadata = enriched.metadata
    assert metadata["reasoning_goal"] == "Analizar clientes"
    assert metadata["fallback_recommended"] is False
    assert "TOP_CLIENTES" in metadata["selected_capabilities"]
    assert metadata["estimated_coverage"] >= 80
    assert "TOP_CLIENTES" in metadata["recommended_plan"]
    assert reasoner_metrics_snapshot()["combination_plans_total"] >= 0


def test_reasoner_recommends_single_capability_for_exact_query(reasoner: CapabilityReasoner) -> None:
    enriched = reasoner.enrich_result(
        question="Muéstrame los principales clientes",
        reasoning_decision=None,
        result=HybridChatResult(
            handled_by="business_pipeline",
            success=True,
            answer="Ranking de clientes.",
            metadata={
                "query_type": "TOP_CLIENTES",
                "reasoning_intent": "business_query",
                "reasoning_confidence": 0.9,
            },
        ),
    )

    assert enriched.metadata["selected_capabilities"] == ["TOP_CLIENTES"]
    assert enriched.metadata["fallback_recommended"] is False
    assert enriched.metadata["estimated_coverage"] >= 85


def test_reasoner_recommends_fallback_for_unrelated_question(reasoner: CapabilityReasoner) -> None:
    enriched = reasoner.enrich_result(
        question="¿Cuál es el sentido de la vida?",
        reasoning_decision=ReasoningDecision(
            intent="unknown",
            confidence=0.4,
            recommended_route="legacy",
            explanation="Fuera de dominio empresarial.",
        ),
        result=HybridChatResult(
            handled_by="guided_fallback",
            success=True,
            answer="No puedo ayudar con eso.",
            metadata={"reasoning_intent": "unknown", "reasoning_confidence": 0.4},
        ),
    )

    assert enriched.metadata["fallback_recommended"] is True
    assert enriched.metadata["estimated_coverage"] < 50
    assert reasoner_metrics_snapshot()["fallback_recommended_total"] == 1


def test_reasoner_disabled_keeps_metadata(reasoner: CapabilityReasoner) -> None:
    engine = CapabilityReasoner(enabled=False)
    original = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="ok",
        metadata={"query_type": "COUNT_CLIENTES"},
    )
    enriched = engine.enrich_result(
        question="¿Cuántos clientes existen?",
        reasoning_decision=None,
        result=original,
    )
    assert enriched.metadata == original.metadata
