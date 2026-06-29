import pytest
from unittest.mock import MagicMock

from app.ai_orchestration.service import is_executive_reasoning_candidate
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_planner import BusinessQueryPlanner
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.business_query_executor import BusinessQueryExecutor
from app.response_engine.deterministic_response_engine import DeterministicResponseEngine
from app.services.semantic_intent_builder import SemanticIntentBuilder


@pytest.mark.parametrize(
    "question",
    [
        "Resumen junio",
        "Resume mayo",
        "¿Cómo ves el negocio?",
        "Dame un panorama ejecutivo",
        "¿Qué riesgos observas?",
        "Analiza el comportamiento del negocio",
    ],
)
def test_executive_pilot_queries_are_reasoning_candidates(question: str) -> None:
    assert is_executive_reasoning_candidate(question) is True


@pytest.mark.parametrize(
    ("question", "expected_type"),
    [
        ("¿Cuántos clientes existen?", BusinessQueryType.COUNT_CLIENTES),
        ("¿Cuántos proveedores existen?", BusinessQueryType.COUNT_PROVEEDORES),
        ("Muéstrame los principales clientes", BusinessQueryType.TOP_CLIENTES),
        ("Top proveedores", BusinessQueryType.TOP_PROVEEDORES),
        ("KPIs", BusinessQueryType.KPIS),
        ("Muéstrame los KPIs", BusinessQueryType.KPIS),
        ("¿Cuántos registros tienes?", BusinessQueryType.DATASET_INFO),
    ],
)
def test_business_pilot_queries_plan_to_expected_type(
    question: str,
    expected_type: BusinessQueryType,
) -> None:
    builder = SemanticIntentBuilder()
    planner = BusinessQueryPlanner()
    intent = builder.build(question)
    query = planner.plan(intent)
    assert query.query_type == expected_type


def test_kpis_executor_and_response_format() -> None:
    system_repo = MagicMock()
    system_repo.get_kpis.return_value = {
        "movimientos": 1000,
        "clientes": 50,
        "proveedores": 30,
        "cuentas": 200,
        "divisas": 3,
    }
    executor = BusinessQueryExecutor(MagicMock(), MagicMock(), system_repo)
    result = executor.execute(BusinessQuery(query_type=BusinessQueryType.KPIS))

    assert result.success is True
    assert result.query_type == "KPIS"

    response = DeterministicResponseEngine().generate(result)
    assert response.success is True
    assert "movimientos" in response.answer.lower()
    assert "50" in response.answer
