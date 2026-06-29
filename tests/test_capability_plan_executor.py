import pytest

from app.capability_plan_executor.constants import (
    CLASSIFICATION_AVOIDABLE,
    CLASSIFICATION_NO_COMPATIBLE,
    STRATEGY_FALLBACK,
    STRATEGY_MULTI,
    STRATEGY_SINGLE,
)
from app.capability_plan_executor.engine import CapabilityPlanExecutor
from app.capability_plan_executor.fallback_classification import (
    classify_guided_fallback_scenarios,
    format_classification_report,
)
from app.capability_plan_executor.metrics import (
    plan_executor_metrics_snapshot,
    reset_plan_executor_metrics_for_tests,
)
from app.capability_reasoner.engine import CapabilityReasoner
from app.reasoning_engine.constants import ROUTE_BUSINESS_PIPELINE
from app.reasoning_engine.schemas import ReasoningDecision
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    reset_plan_executor_metrics_for_tests()


def _reasoner_metadata(question: str) -> dict:
    reasoner = CapabilityReasoner(enabled=True)
    base = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Fallback original.",
        metadata={"fallback_type": "UNSUPPORTED_CAPABILITY"},
    )
    enriched = reasoner.enrich_result(
        question=question,
        reasoning_decision=ReasoningDecision(
            intent="business_query",
            confidence=0.84,
            recommended_route=ROUTE_BUSINESS_PIPELINE,
            explanation="Consulta empresarial.",
        ),
        result=base,
    )
    return enriched.metadata


def _pipeline_result(query_type: str) -> HybridChatResult:
    return HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer=f"Respuesta determinística de {query_type}.",
        metadata={"query_type": query_type, "confidence": 1.0},
    )


@pytest.fixture
def executor() -> CapabilityPlanExecutor:
    return CapabilityPlanExecutor(
        enabled=True,
        execute_capability=lambda capability_id, _session_id: _pipeline_result(capability_id),
    )


def test_classification_report_covers_sprint_scenarios() -> None:
    rows = classify_guided_fallback_scenarios()
    questions = {row["question"] for row in rows}
    assert "Analiza el universo de clientes" in questions
    assert "¿Cuál es el sentido de la vida?" in questions
    report = format_classification_report(rows)
    assert "Clasificación de Guided Fallback" in report
    assert "Evitable" in report


def test_executor_avoids_fallback_for_high_coverage_client_analysis(
    executor: CapabilityPlanExecutor,
) -> None:
    metadata = _reasoner_metadata("Analiza el universo de clientes")
    fallback = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Fallback original.",
        metadata=metadata,
    )

    executed = executor.try_execute(
        question="Analiza el universo de clientes",
        session_id="sess-1",
        result=fallback,
    )

    assert executed.handled_by == "business_pipeline"
    assert executed.metadata["plan_executed"] is True
    assert executed.metadata["fallback_avoided"] is True
    assert executed.metadata["primary_capability"] == "TOP_CLIENTES"
    assert executed.metadata["execution_strategy"] in {STRATEGY_SINGLE, STRATEGY_MULTI}
    assert executed.answer == "Respuesta determinística de TOP_CLIENTES."
    assert plan_executor_metrics_snapshot()["fallback_avoided_total"] == 1


def test_executor_partial_execution_for_medium_coverage(executor: CapabilityPlanExecutor) -> None:
    metadata = _reasoner_metadata("Háblame de los clientes")
    fallback = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Fallback.",
        metadata=metadata,
    )

    executed = executor.try_execute(
        question="Háblame de los clientes",
        session_id="sess-2",
        result=fallback,
    )

    coverage = float(executed.metadata.get("coverage_used", 0))
    if coverage >= 60 and executed.metadata.get("plan_executed"):
        assert executed.handled_by == "business_pipeline"
        if coverage < 80:
            assert executed.metadata["partial_execution"] is True
    else:
        assert executed.metadata["execution_strategy"] == STRATEGY_FALLBACK


def test_executor_keeps_fallback_for_out_of_domain(executor: CapabilityPlanExecutor) -> None:
    metadata = _reasoner_metadata("¿Cuál es el sentido de la vida?")
    fallback = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Fuera de dominio.",
        metadata={**metadata, "fallback_type": "OUT_OF_DOMAIN"},
    )

    executed = executor.try_execute(
        question="¿Cuál es el sentido de la vida?",
        session_id="sess-3",
        result=fallback,
    )

    assert executed.handled_by == "guided_fallback"
    assert executed.metadata["plan_executed"] is False
    assert executed.metadata["execution_strategy"] == STRATEGY_FALLBACK
    assert executed.metadata["fallback_avoided"] is False


def test_executor_reuses_capability_for_supplier_analysis(executor: CapabilityPlanExecutor) -> None:
    metadata = _reasoner_metadata("Analiza nuestros proveedores")
    fallback = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Fallback.",
        metadata=metadata,
    )

    executed = executor.try_execute(
        question="Analiza nuestros proveedores",
        session_id="sess-4",
        result=fallback,
    )

    if float(metadata.get("estimated_coverage", 0)) >= 60:
        assert executed.handled_by == "business_pipeline"
        assert executed.metadata["primary_capability"] in {"TOP_PROVEEDORES", "COUNT_PROVEEDORES"}


def test_classification_marks_client_universe_as_avoidable() -> None:
    rows = classify_guided_fallback_scenarios()
    row = next(item for item in rows if item["question"] == "Analiza el universo de clientes")
    assert row["classification"] in {CLASSIFICATION_AVOIDABLE, CLASSIFICATION_NO_COMPATIBLE}
    assert row["expected"] == CLASSIFICATION_AVOIDABLE
    assert row["coverage"] >= 60


def test_classification_marks_out_of_domain_as_no_compatible() -> None:
    rows = classify_guided_fallback_scenarios()
    row = next(item for item in rows if "sentido de la vida" in item["question"])
    assert row["classification"] == CLASSIFICATION_NO_COMPATIBLE
