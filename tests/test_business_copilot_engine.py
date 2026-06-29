from unittest.mock import MagicMock

import pytest

from app.ai_orchestration.providers.mock_provider import MockProvider
from app.business_copilot.engine import BusinessCopilotEngine
from app.business_copilot.metrics import copilot_metrics_snapshot, reset_copilot_metrics_for_tests
from app.query_engine.query_types import BusinessQueryType
from app.schemas.hybrid_chat import HybridChatResult
from app.suggested_questions.schemas import SuggestedQuestionsResult
from app.core import settings as settings_module


@pytest.fixture(autouse=True)
def enable_copilot(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings_module.settings, "BUSINESS_COPILOT_ENABLED", True)


@pytest.fixture
def engine() -> BusinessCopilotEngine:
    return BusinessCopilotEngine(llm_provider=MockProvider())


def _business_result(
    *,
    answer: str,
    query_type: str,
    handled_by: str = "business_pipeline",
) -> HybridChatResult:
    return HybridChatResult(
        handled_by=handled_by,
        success=True,
        answer=answer,
        suggestions=SuggestedQuestionsResult(
            questions=["¿Cuántos proveedores existen?"],
            source="type_rules",
            confidence=0.9,
        ),
        metadata={"query_type": query_type, "confidence": 0.95},
    )


def test_copilot_generates_contextual_proposals_for_top_clientes(
    engine: BusinessCopilotEngine,
) -> None:
    reset_copilot_metrics_for_tests()
    base = _business_result(
        answer="Los principales clientes identificados son: A, B, C",
        query_type=BusinessQueryType.TOP_CLIENTES.value,
    )
    result = engine.enrich("Muéstrame los principales clientes", base, session_id="sess-top")

    assert result.answer == base.answer
    assert result.suggestions == base.suggestions
    proposals = result.metadata["business_copilot_proposals"]
    assert proposals
    assert any("concentración" in proposal["title"].lower() for proposal in proposals)
    assert result.metadata["proposals_generated"] is True


def test_copilot_proposals_differ_between_query_types(engine: BusinessCopilotEngine) -> None:
    top_clientes = engine.enrich(
        "Top clientes",
        _business_result(
            answer="Ranking clientes",
            query_type=BusinessQueryType.TOP_CLIENTES.value,
        ),
        session_id="sess-a",
    )
    kpis = engine.enrich(
        "KPIs",
        _business_result(
            answer="Movimientos y clientes",
            query_type=BusinessQueryType.KPIS.value,
        ),
        session_id="sess-b",
    )

    top_titles = {item["title"] for item in top_clientes.metadata["business_copilot_proposals"]}
    kpi_titles = {item["title"] for item in kpis.metadata["business_copilot_proposals"]}
    assert top_titles != kpi_titles


def test_copilot_skips_repeated_questions(engine: BusinessCopilotEngine) -> None:
    session_id = "sess-repeat"
    first = engine.enrich(
        "Muéstrame los principales clientes",
        _business_result(
            answer="Ranking clientes",
            query_type=BusinessQueryType.TOP_CLIENTES.value,
        ),
        session_id=session_id,
    )
    first_query = first.metadata["business_copilot_proposals"][0]["query"]

    second = engine.enrich(
        "Muéstrame los principales clientes",
        _business_result(
            answer="Ranking clientes",
            query_type=BusinessQueryType.TOP_CLIENTES.value,
        ),
        session_id=session_id,
    )
    second_queries = [
        item["query"] for item in second.metadata.get("business_copilot_proposals", [])
    ]
    assert first_query not in second_queries


def test_copilot_fallback_preserves_suggestions_on_llm_failure() -> None:
    reset_copilot_metrics_for_tests()
    failing_provider = MagicMock()
    failing_provider.generate_response.side_effect = RuntimeError("llm down")
    failing_provider.provider_name.return_value = "mock"
    failing_provider.model_name = "mock-v1"

    engine = BusinessCopilotEngine(llm_provider=failing_provider)
    base = _business_result(
        answer="KPIs del dataset",
        query_type=BusinessQueryType.KPIS.value,
    )
    result = engine.enrich("KPIs", base, session_id="sess-fallback")

    assert result.answer == base.answer
    assert result.suggestions == base.suggestions
    assert result.metadata["proposals_generated"] is True
    assert result.metadata["copilot_fallback_used"] is True
    assert result.metadata["business_copilot_proposals"]
    metrics = copilot_metrics_snapshot()
    assert metrics["fallbacks_used"] == 1


def test_copilot_supports_executive_reasoning(engine: BusinessCopilotEngine) -> None:
    base = HybridChatResult(
        handled_by="executive_reasoning",
        success=True,
        answer="Resumen ejecutivo de junio con hallazgos.",
        metadata={},
    )
    result = engine.enrich("Resumen junio", base, session_id="sess-exec")
    proposals = result.metadata["business_copilot_proposals"]
    assert proposals
    assert any("clientes" in proposal["query"].lower() for proposal in proposals)


def test_copilot_disabled_returns_original(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings_module.settings, "BUSINESS_COPILOT_ENABLED", False)
    engine = BusinessCopilotEngine(llm_provider=MockProvider())
    base = _business_result(
        answer="Ranking",
        query_type=BusinessQueryType.TOP_CLIENTES.value,
    )
    result = engine.enrich("Top clientes", base)
    assert result == base
