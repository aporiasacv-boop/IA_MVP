from unittest.mock import MagicMock

import pytest

from app.ai_orchestration.providers.mock_provider import MockProvider
from app.core import settings as settings_module
from app.executive_insight.engine import ExecutiveInsightEngine
from app.executive_insight.metrics import insight_metrics_snapshot, reset_insight_metrics_for_tests
from app.query_engine.query_types import BusinessQueryType
from app.schemas.hybrid_chat import HybridChatResult
from app.suggested_questions.schemas import SuggestedQuestionsResult


@pytest.fixture(autouse=True)
def enable_insight(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings_module.settings, "EXECUTIVE_INSIGHT_ENABLED", True)


@pytest.fixture
def engine() -> ExecutiveInsightEngine:
    return ExecutiveInsightEngine(llm_provider=MockProvider())


def _business_result(
    *,
    answer: str = "Existen 48 clientes activos en el dataset.",
    query_type: str = BusinessQueryType.COUNT_CLIENTES.value,
) -> HybridChatResult:
    return HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer=answer,
        suggestions=SuggestedQuestionsResult(
            questions=["¿Cuántos proveedores existen?"],
            source="type_rules",
            confidence=0.9,
        ),
        metadata={"query_type": query_type, "confidence": 0.95},
    )


def test_insight_enriches_eligible_business_response(engine: ExecutiveInsightEngine) -> None:
    reset_insight_metrics_for_tests()
    base = _business_result()
    result = engine.enrich("¿Cuántos clientes existen?", base)

    assert result.answer == base.answer
    assert result.metadata["insight_generated"] is True
    assert result.metadata["fallback_used"] is False
    assert "executive_insight" in result.metadata
    insight = result.metadata["executive_insight"]
    assert insight["executive_summary"]
    assert insight["business_interpretation"]
    assert result.metadata["provider"] == "mock"
    assert result.metadata["insight_generation_ms"] >= 0
    metrics = insight_metrics_snapshot()
    assert metrics["insights_generated"] == 1


def test_insight_skips_non_eligible_handled_by(engine: ExecutiveInsightEngine) -> None:
    base = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Respuesta guiada",
        metadata={"query_type": BusinessQueryType.COUNT_CLIENTES.value},
    )
    result = engine.enrich("¿Cuántos clientes existen?", base)
    assert result == base
    assert "executive_insight" not in result.metadata


def test_insight_skips_non_eligible_query_type(engine: ExecutiveInsightEngine) -> None:
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Capacidades del sistema",
        metadata={"query_type": "SYSTEM_CAPABILITIES"},
    )
    result = engine.enrich("¿Qué puedes hacer?", base)
    assert result == base


def test_insight_fallback_preserves_answer_on_llm_failure() -> None:
    reset_insight_metrics_for_tests()
    failing_provider = MagicMock()
    failing_provider.generate_response.side_effect = RuntimeError("llm down")
    failing_provider.provider_name.return_value = "mock"
    failing_provider.model_name = "mock-v1"

    engine = ExecutiveInsightEngine(llm_provider=failing_provider)
    base = _business_result(answer="Top 5 clientes: A, B, C, D, E")
    result = engine.enrich("Top clientes", base)

    assert result.answer == base.answer
    assert result.metadata["insight_generated"] is False
    assert result.metadata["fallback_used"] is True
    assert "executive_insight" not in result.metadata
    metrics = insight_metrics_snapshot()
    assert metrics["fallbacks_used"] == 1


def test_insight_merges_next_questions(engine: ExecutiveInsightEngine) -> None:
    base = _business_result(query_type=BusinessQueryType.TOP_CLIENTES.value)
    result = engine.enrich("Top clientes", base)

    assert result.suggestions is not None
    assert any("porcentaje" in question.lower() for question in result.suggestions.questions)


def test_insight_disabled_returns_original(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings_module.settings, "EXECUTIVE_INSIGHT_ENABLED", False)
    engine = ExecutiveInsightEngine(llm_provider=MockProvider())
    base = _business_result()
    result = engine.enrich("¿Cuántos clientes existen?", base)
    assert result == base
