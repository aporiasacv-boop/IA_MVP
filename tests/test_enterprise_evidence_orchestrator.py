import pytest

from app.enterprise_evidence_orchestrator.engine import EnterpriseEvidenceOrchestrator
from app.enterprise_evidence_orchestrator.metrics import (
    orchestrator_metrics_snapshot,
    reset_orchestrator_metrics_for_tests,
)
from app.enterprise_evidence_orchestrator.plan_analysis import (
    analyze_plan_feasibility,
    format_plan_feasibility_report,
)
from app.enterprise_evidence_planner.engine import EnterpriseEvidencePlanner
from app.enterprise_evidence_planner.planner import build_evidence_plan
from app.reasoning_engine.constants import ROUTE_BUSINESS_PIPELINE
from app.reasoning_engine.schemas import ReasoningDecision
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    reset_orchestrator_metrics_for_tests()


def _pipeline_result(query_type: str) -> HybridChatResult:
    return HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer=f"Evidencia de {query_type}.",
        metadata={"query_type": query_type, "confidence": 0.95},
    )


def _planner_metadata(question: str) -> dict:
    planner = EnterpriseEvidencePlanner(enabled=True)
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Respuesta original.",
        metadata={"reasoning_intent": "business_query"},
    )
    enriched = planner.enrich_result(
        question=question,
        reasoning_decision=ReasoningDecision(
            intent="business_query",
            confidence=0.9,
            recommended_route=ROUTE_BUSINESS_PIPELINE,
            explanation="Consulta empresarial.",
        ),
        result=base,
    )
    return enriched.metadata


@pytest.fixture
def orchestrator() -> EnterpriseEvidenceOrchestrator:
    calls: list[str] = []

    def runner(capability_id: str, _session_id: str | None) -> HybridChatResult:
        calls.append(capability_id)
        return _pipeline_result(capability_id)

    engine = EnterpriseEvidenceOrchestrator(
        enabled=True,
        execute_capability=runner,
    )
    engine._calls = calls  # type: ignore[attr-defined]
    return engine


def test_plan_feasibility_all_sprint_capabilities_executable() -> None:
    cartera = analyze_plan_feasibility("¿Cómo ves nuestra cartera?")
    assert cartera["fully_executable"] is True
    assert "TOP_CLIENTES" in cartera["required_capabilities"]
    assert "KPIS" in cartera["required_capabilities"]
    assert "DATA_COVERAGE" in cartera["required_capabilities"]

    proveedores = analyze_plan_feasibility("Analiza nuestros proveedores")
    assert proveedores["fully_executable"] is True
    assert "TOP_PROVEEDORES" in proveedores["required_capabilities"]
    assert "COUNT_PROVEEDORES" in proveedores["required_capabilities"]
    assert "MAX_PROVEEDOR_MES" in proveedores["required_capabilities"]

    report = format_plan_feasibility_report()
    assert "Análisis EnterpriseEvidencePlan" in report


def test_cartera_builds_package_with_expected_capabilities(orchestrator: EnterpriseEvidenceOrchestrator) -> None:
    metadata = _planner_metadata("¿Cómo ves nuestra cartera?")
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Respuesta original.",
        metadata=metadata,
    )

    result = orchestrator.orchestrate(question="¿Cómo ves nuestra cartera?", session_id="s1", result=base)

    assert result.answer == "Respuesta original."
    assert result.handled_by == "business_pipeline"
    package = result.metadata["enterprise_evidence_package"]
    capabilities = {item["capability"] for item in package["evidence_items"]}
    assert {"TOP_CLIENTES", "KPIS", "DATA_COVERAGE"}.issubset(capabilities)
    assert result.metadata["evidence_count"] == 3
    assert len(orchestrator._calls) == 3  # type: ignore[attr-defined]


def test_proveedores_builds_package_with_expected_capabilities(orchestrator: EnterpriseEvidenceOrchestrator) -> None:
    metadata = _planner_metadata("Analiza nuestros proveedores")
    base = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Fallback original.",
        metadata=metadata,
    )

    result = orchestrator.orchestrate(question="Analiza nuestros proveedores", session_id="s1", result=base)

    assert result.answer == "Fallback original."
    assert result.handled_by == "guided_fallback"
    package = result.metadata["enterprise_evidence_package"]
    capabilities = {item["capability"] for item in package["evidence_items"]}
    assert capabilities == {"TOP_PROVEEDORES", "COUNT_PROVEEDORES", "MAX_PROVEEDOR_MES"}


def test_count_clientes_executes_single_capability(orchestrator: EnterpriseEvidenceOrchestrator) -> None:
    metadata = _planner_metadata("¿Cuántos clientes existen?")
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="42 clientes.",
        metadata=metadata,
    )

    result = orchestrator.orchestrate(question="¿Cuántos clientes existen?", session_id="s1", result=base)

    package = result.metadata["enterprise_evidence_package"]
    assert package["evidence_items"][0]["capability"] == "COUNT_CLIENTES"
    assert orchestrator._calls == ["COUNT_CLIENTES"]  # type: ignore[attr-defined]


def test_sentido_de_la_vida_skips_package(orchestrator: EnterpriseEvidenceOrchestrator) -> None:
    plan = build_evidence_plan(
        question="¿Cuál es el sentido de la vida?",
        intent="business_query",
        explanation=None,
    )
    base = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="No puedo responder eso.",
        metadata={
            "fallback_type": "UNKNOWN",
            **plan.observability_metadata(1.0),
        },
    )

    result = orchestrator.orchestrate(
        question="¿Cuál es el sentido de la vida?",
        session_id="s1",
        result=base,
    )

    assert "enterprise_evidence_package" not in result.metadata
    assert result.answer == "No puedo responder eso."
    assert result.handled_by == "guided_fallback"
    assert orchestrator_metrics_snapshot()["skipped_total"] == 1


def test_sequential_execution_preserves_business_response(orchestrator: EnterpriseEvidenceOrchestrator) -> None:
    metadata = _planner_metadata("¿Cómo ves nuestra cartera?")
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Respuesta visible intacta.",
        metadata=metadata,
    )

    result = orchestrator.orchestrate(question="¿Cómo ves nuestra cartera?", session_id="s1", result=base)

    for item in result.metadata["enterprise_evidence_package"]["evidence_items"]:
        assert item["source"] == "business_pipeline"
        assert item["answer"].startswith("Evidencia de ")
        assert item["success"] is True


def test_partial_failure_continues_and_reports_failed_capabilities() -> None:
    def flaky_runner(capability_id: str, _session_id: str | None) -> HybridChatResult:
        if capability_id == "KPIS":
            return HybridChatResult(
                handled_by="guided_fallback",
                success=False,
                answer="Fallo.",
                metadata={"query_type": capability_id},
            )
        return _pipeline_result(capability_id)

    orchestrator = EnterpriseEvidenceOrchestrator(enabled=True, execute_capability=flaky_runner)
    metadata = _planner_metadata("¿Cómo ves nuestra cartera?")
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Respuesta original.",
        metadata=metadata,
    )

    result = orchestrator.orchestrate(question="¿Cómo ves nuestra cartera?", session_id="s1", result=base)

    assert "KPIS" in result.metadata["failed_capabilities"]
    assert "TOP_CLIENTES" in result.metadata["completed_capabilities"]
    assert result.metadata["evidence_count"] == 2
    assert result.answer == "Respuesta original."
    assert orchestrator_metrics_snapshot()["partial_packages_total"] == 1


def test_duplicate_capability_executed_once() -> None:
    calls: list[str] = []

    def runner(capability_id: str, _session_id: str | None) -> HybridChatResult:
        calls.append(capability_id)
        return _pipeline_result(capability_id)

    orchestrator = EnterpriseEvidenceOrchestrator(enabled=True, execute_capability=runner)
    plan = build_evidence_plan(
        question="¿Cuál es el riesgo comercial?",
        intent="business_query",
        explanation=None,
    )
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Respuesta.",
        metadata=plan.observability_metadata(1.0),
    )

    orchestrator.orchestrate(question="¿Cuál es el riesgo comercial?", session_id="s1", result=base)

    top_calls = [cap for cap in calls if cap == "TOP_CLIENTES"]
    assert len(top_calls) == 1
