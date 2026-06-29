import pytest

from app.ai_orchestration.providers.mock_provider import MockProvider
from app.enterprise_evidence_orchestrator.schemas import (
    CollectedEvidenceItem,
    EnterpriseEvidencePackage,
)
from app.executive_reasoning_v2.constants import HANDLED_BY_EXECUTIVE_REASONING_V2
from app.executive_reasoning_v2.engine import ExecutiveReasoningV2Engine
from app.executive_reasoning_v2.metrics import (
    reasoning_v2_metrics_snapshot,
    reset_reasoning_v2_metrics_for_tests,
)
from app.executive_reasoning_v2.parser import parse_reasoning_v2_response
from app.executive_reasoning_v2.prompt import build_executive_reasoning_v2_prompt
from app.executive_insight.engine import ExecutiveInsightEngine
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    reset_reasoning_v2_metrics_for_tests()


def _package(
    *,
    goal: str,
    capabilities: list[tuple[str, str, str]],
    coverage: float = 92.0,
    missing: list[str] | None = None,
) -> dict:
    items = [
        CollectedEvidenceItem(
            evidence_id=evidence_id,
            evidence_label=label,
            capability=capability,
            query_type=capability,
            source="business_pipeline",
            answer=f"Evidencia validada de {capability}.",
            confidence=0.95,
            success=True,
        )
        for evidence_id, label, capability in capabilities
    ]
    pkg = EnterpriseEvidencePackage(
        business_goal=goal,
        evidence_items=items,
        coverage=coverage,
        sources=["business_pipeline"],
        query_types=[capability for _, _, capability in capabilities],
        execution_summary=f"{len(items)} evidencias recolectadas.",
        missing_evidence=missing or [],
        confidence=0.95,
    )
    return {
        "enterprise_evidence_package": pkg.model_dump(),
        "business_goal": goal,
        "package_coverage": coverage,
    }


@pytest.fixture
def engine() -> ExecutiveReasoningV2Engine:
    return ExecutiveReasoningV2Engine(llm_provider=MockProvider(), enabled=True)


def test_prompt_uses_evidence_not_direct_answer() -> None:
    package = EnterpriseEvidencePackage.model_validate(
        _package(
            goal="Analizar salud comercial",
            capabilities=[
                ("principales_clientes", "Principales clientes", "TOP_CLIENTES"),
                ("kpis_negocio", "Indicadores clave", "KPIS"),
            ],
        )["enterprise_evidence_package"]
    )
    prompt = build_executive_reasoning_v2_prompt(
        original_question="¿Cómo ves nuestra cartera?",
        business_goal="Analizar salud comercial",
        evidence_package=package,
    )
    assert "NO respondas la pregunta del usuario de forma directa" in prompt
    assert "TOP_CLIENTES" in prompt
    assert "Evidencia validada de TOP_CLIENTES" in prompt


def test_parser_accepts_valid_sections() -> None:
    parsed = parse_reasoning_v2_response(
        '{"executive_summary":"Resumen","findings":["Hallazgo 1"],"recommendations":["Acción"]}'
    )
    assert parsed is not None
    assert parsed.executive_summary == "Resumen"
    assert parsed.generated_sections() == ["executive_summary", "findings", "recommendations"]


def test_cartera_replaces_guided_fallback_with_executive_answer(engine: ExecutiveReasoningV2Engine) -> None:
    metadata = _package(
        goal="Analizar salud comercial",
        capabilities=[
            ("principales_clientes", "Principales clientes", "TOP_CLIENTES"),
            ("kpis_negocio", "Indicadores clave", "KPIS"),
            ("cobertura_temporal", "Cobertura temporal", "DATA_COVERAGE"),
        ],
    )
    base = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="No pude responder con el pipeline.",
        metadata=metadata,
    )

    result = engine.enrich("¿Cómo ves nuestra cartera?", base, session_id="s1")

    assert result.handled_by == HANDLED_BY_EXECUTIVE_REASONING_V2
    assert "Con la evidencia disponible puedo concluir" in result.answer
    assert result.metadata["executive_reasoning_v2_enabled"] is True
    assert result.metadata["evidence_package_used"] is True
    assert "principales_clientes" in result.metadata["evidence_items_used"]
    assert result.metadata["reasoning_sections_generated"]
    assert result.metadata["executive_insight"]["source"] == "executive_reasoning_v2"


def test_count_clientes_preserves_deterministic_answer(engine: ExecutiveReasoningV2Engine) -> None:
    deterministic = "Existen 48 clientes activos."
    metadata = _package(
        goal="Contar clientes registrados",
        capabilities=[("conteo_clientes", "Conteo de clientes", "COUNT_CLIENTES")],
        coverage=88.0,
    )
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer=deterministic,
        metadata={**metadata, "query_type": "COUNT_CLIENTES"},
    )

    result = engine.enrich("¿Cuántos clientes existen?", base, session_id="s1")

    assert result.answer == deterministic
    assert result.handled_by == "business_pipeline"
    assert result.metadata["executive_reasoning_v2_generated"] is True
    assert result.metadata["executive_insight"]["executive_summary"]


def test_proveedores_package_generates_sections(engine: ExecutiveReasoningV2Engine) -> None:
    metadata = _package(
        goal="Analizar base de proveedores",
        capabilities=[
            ("principales_proveedores", "Principales proveedores", "TOP_PROVEEDORES"),
            ("conteo_proveedores", "Conteo de proveedores", "COUNT_PROVEEDORES"),
            ("movimiento_proveedor", "Movimiento destacado", "MAX_PROVEEDOR_MES"),
        ],
    )
    base = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Fallback proveedores.",
        metadata=metadata,
    )

    result = engine.enrich("Analiza nuestros proveedores", base, session_id="s1")

    assert result.metadata["evidence_coverage"] >= 60
    sections = result.metadata["reasoning_sections_generated"]
    assert "executive_summary" in sections
    assert reasoning_v2_metrics_snapshot()["generated_total"] == 1


def test_skips_without_evidence_package(engine: ExecutiveReasoningV2Engine) -> None:
    base = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="¿Cuál es el sentido de la vida?",
        metadata={"fallback_type": "UNKNOWN"},
    )

    result = engine.enrich("¿Cuál es el sentido de la vida?", base, session_id="s1")

    assert "executive_reasoning_v2" not in result.metadata
    assert reasoning_v2_metrics_snapshot()["skipped_total"] == 1


def test_executive_insight_skips_when_v2_already_ran(engine: ExecutiveReasoningV2Engine) -> None:
    insight_engine = ExecutiveInsightEngine(llm_provider=MockProvider(), enabled=True)
    metadata = _package(
        goal="Contar clientes registrados",
        capabilities=[("conteo_clientes", "Conteo de clientes", "COUNT_CLIENTES")],
    )
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Existen 48 clientes activos.",
        metadata={**metadata, "query_type": "COUNT_CLIENTES"},
    )

    with_v2 = engine.enrich("¿Cuántos clientes existen?", base, session_id="s1")
    with_insight = insight_engine.enrich("¿Cuántos clientes existen?", with_v2, session_id="s1")

    assert with_insight.metadata.get("insight_source") == "executive_reasoning_v2"
    assert with_insight.metadata["executive_insight"]["source"] == "executive_reasoning_v2"


def test_top_clientes_preserves_pipeline_answer(engine: ExecutiveReasoningV2Engine) -> None:
    deterministic = "1. Cliente A — 120 movimientos"
    metadata = _package(
        goal="Ranking de clientes",
        capabilities=[("principales_clientes", "Principales clientes", "TOP_CLIENTES")],
    )
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer=deterministic,
        metadata={**metadata, "query_type": "TOP_CLIENTES"},
    )

    result = engine.enrich("Top clientes", base, session_id="s1")

    assert result.answer == deterministic
    assert "executive_insight" in result.metadata
