from unittest.mock import MagicMock

import pytest

from app.ai_orchestration.providers.mock_provider import MockProvider
from app.core import settings as settings_module
from app.executive_advisor.engine import ExecutiveAdvisorEngine
from app.executive_advisor.metrics import advisor_metrics_snapshot, reset_advisor_metrics_for_tests
from app.executive_advisor.schemas import AdvisorInput
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture(autouse=True)
def enable_advisor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings_module.settings, "EXECUTIVE_ADVISOR_ENABLED", True)


@pytest.fixture
def engine() -> ExecutiveAdvisorEngine:
    return ExecutiveAdvisorEngine(llm_provider=MockProvider())


def test_advisor_builds_agenda_with_items(engine: ExecutiveAdvisorEngine) -> None:
    reset_advisor_metrics_for_tests()
    advisor_input = AdvisorInput(
        dataset_summary={
            "clientes": 48,
            "proveedores": 32,
            "registros": 12500,
            "fecha_minima": "2024-01-01",
            "fecha_maxima": "2024-06-30",
        },
        financial_scenario={"name": "Producción", "description": "Operación productiva estándar."},
    )
    response = engine.build_agenda(advisor_input)

    assert response.advisor_items > 0
    assert response.agenda.greeting
    assert response.agenda.items[0].suggested_query
    assert response.advisor_fallback_used is False
    metrics = advisor_metrics_snapshot()
    assert metrics["agendas_generated"] == 1


def test_advisor_fallback_always_returns_agenda() -> None:
    reset_advisor_metrics_for_tests()
    failing_provider = MagicMock()
    failing_provider.generate_response.side_effect = RuntimeError("llm down")
    failing_provider.provider_name.return_value = "mock"
    failing_provider.model_name = "mock-v1"

    engine = ExecutiveAdvisorEngine(llm_provider=failing_provider)
    response = engine.build_agenda(
        AdvisorInput(dataset_summary={"clientes": 10, "registros": 1000}),
    )

    assert response.advisor_items > 0
    assert response.advisor_fallback_used is True


def test_advisor_enrich_preserves_business_answer(engine: ExecutiveAdvisorEngine) -> None:
    base = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Actualmente existen 48 clientes registrados.",
        metadata={
            "query_type": "COUNT_CLIENTES",
            "executive_insight": {"executive_summary": "Resumen validado."},
            "business_copilot_proposals": [
                {
                    "title": "Identificar clientes principales",
                    "query": "Muéstrame los principales clientes",
                    "rationale": "Siguiente paso natural.",
                    "action_label": "Profundizar",
                    "proposal_type": "profundizar",
                }
            ],
        },
    )
    advisor_input = AdvisorInput(
        dataset_summary={"clientes": 48},
        business_copilot_proposals=base.metadata["business_copilot_proposals"],
        executive_insight=base.metadata["executive_insight"],
        last_query_type="COUNT_CLIENTES",
        last_answer=base.answer,
    )
    result = engine.enrich(advisor_input, base)

    assert result.answer == base.answer
    assert "executive_advisor_agenda" in result.metadata
    assert result.metadata["advisor_items"] > 0


def test_advisor_fallback_agenda_varies_with_context() -> None:
    failing_provider = MagicMock()
    failing_provider.generate_response.side_effect = RuntimeError("llm down")
    failing_provider.provider_name.return_value = "mock"
    failing_provider.model_name = "mock-v1"
    engine = ExecutiveAdvisorEngine(llm_provider=failing_provider)

    kpis_focus = engine.build_agenda(
        AdvisorInput(last_query_type="KPIS", dataset_summary={"registros": 9000}),
    )
    top_focus = engine.build_agenda(
        AdvisorInput(
            last_query_type="TOP_CLIENTES",
            dataset_summary={"clientes": 48},
        ),
    )
    assert kpis_focus.advisor_fallback_used is True
    assert top_focus.advisor_fallback_used is True
    assert {item.suggested_query for item in kpis_focus.agenda.items} != {
        item.suggested_query for item in top_focus.agenda.items
    }
