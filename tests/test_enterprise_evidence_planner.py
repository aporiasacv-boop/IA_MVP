import pytest

from app.enterprise_evidence_planner.engine import EnterpriseEvidencePlanner
from app.enterprise_evidence_planner.metrics import (
    evidence_planner_metrics_snapshot,
    reset_evidence_planner_metrics_for_tests,
)
from app.enterprise_evidence_planner.open_query_analysis import (
    SPRINT_OPEN_QUERIES,
    analyze_open_queries,
    format_open_query_analysis,
)
from app.enterprise_evidence_planner.planner import build_evidence_plan
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    reset_evidence_planner_metrics_for_tests()


@pytest.fixture
def planner() -> EnterpriseEvidencePlanner:
    return EnterpriseEvidencePlanner(enabled=True)


def test_open_query_analysis_includes_sprint_questions() -> None:
    rows = analyze_open_queries()
    assert len(rows) == len(SPRINT_OPEN_QUERIES)
    report = format_open_query_analysis(rows)
    assert "Analizar salud comercial" in report
    assert "TOP_CLIENTES" in report


def test_cartera_generates_multi_evidence_plan() -> None:
    plan = build_evidence_plan(
        question="¿Cómo ves nuestra cartera?",
        intent="business_query",
        explanation="Consulta ejecutiva sobre cartera.",
    )

    assert plan.business_goal == "Analizar salud comercial"
    assert len(plan.required_evidence) >= 3
    assert "TOP_CLIENTES" in plan.required_capabilities
    assert "KPIS" in plan.required_capabilities
    assert "DATA_COVERAGE" in plan.required_capabilities
    assert plan.estimated_coverage >= 90
    assert len(plan.execution_order) >= 3


def test_simple_query_generates_single_evidence() -> None:
    plan = build_evidence_plan(
        question="¿Cuántos clientes existen?",
        intent="business_query",
        explanation=None,
    )

    assert len(plan.required_evidence) == 1
    assert plan.required_capabilities == ["COUNT_CLIENTES"]
    assert plan.execution_order == ["COUNT_CLIENTES"]
    assert plan.estimated_coverage >= 85


def test_enrich_result_does_not_change_answer(planner: EnterpriseEvidencePlanner) -> None:
    original = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Respuesta original.",
        metadata={"reasoning_intent": "business_query"},
    )

    enriched = planner.enrich_result(
        question="Analiza el universo de clientes.",
        reasoning_decision=None,
        result=original,
    )

    assert enriched.answer == original.answer
    assert enriched.handled_by == original.handled_by
    assert enriched.metadata["business_goal"]
    assert enriched.metadata["required_evidence"]
    assert enriched.metadata["planning_time_ms"] >= 0
    assert evidence_planner_metrics_snapshot()["multi_evidence_plans"] >= 1


def test_proveedores_open_query_uses_supplier_evidence() -> None:
    plan = build_evidence_plan(
        question="Analiza nuestros proveedores",
        intent="business_query",
        explanation=None,
    )

    assert plan.business_goal == "Analizar base de proveedores"
    assert "TOP_PROVEEDORES" in plan.required_capabilities
    assert len(plan.required_evidence) >= 2


def test_concentracion_plan_targets_client_evidence() -> None:
    plan = build_evidence_plan(
        question="¿Tenemos concentración de clientes?",
        intent="business_query",
        explanation=None,
    )

    assert "concentración" in plan.business_goal.lower() or "concentracion" in plan.business_goal.lower()
    assert "TOP_CLIENTES" in plan.required_capabilities
    assert len(plan.required_evidence) >= 2


def test_planner_disabled_keeps_metadata() -> None:
    engine = EnterpriseEvidencePlanner(enabled=False)
    original = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="ok",
        metadata={},
    )
    enriched = engine.enrich_result(
        question="¿Cómo ves nuestra cartera?",
        reasoning_decision=None,
        result=original,
    )
    assert enriched.metadata == original.metadata
