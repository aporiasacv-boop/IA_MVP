import pytest

from app.reasoning_engine.constants import (
    ROUTE_BUSINESS_PIPELINE,
    ROUTE_CLARIFICATION,
    ROUTE_CONVERSATION,
    ROUTE_EXECUTIVE_ANALYSIS,
    ROUTE_INSTITUTIONAL_KNOWLEDGE,
)
from app.reasoning_engine.fallback import rule_based_decision
from app.reasoning_engine.metrics import get_metrics, reset_metrics
from app.reasoning_engine.parser import parse_reasoning_response


@pytest.mark.parametrize(
    ("message", "expected_route"),
    [
        ("Hola", ROUTE_CONVERSATION),
        ("¿Cómo estás?", ROUTE_CONVERSATION),
        ("¿Cuántos clientes existen?", ROUTE_BUSINESS_PIPELINE),
        ("Resume junio", ROUTE_EXECUTIVE_ANALYSIS),
        ("¿Qué puedes hacer?", ROUTE_INSTITUTIONAL_KNOWLEDGE),
        ("No entiendo", ROUTE_CLARIFICATION),
    ],
)
def test_rule_based_decision_routes(message: str, expected_route: str) -> None:
    decision = rule_based_decision(message)
    assert decision.recommended_route == expected_route


def test_parse_reasoning_response_accepts_json() -> None:
    raw = (
        '{"intent":"business_query","confidence":0.94,'
        '"recommended_route":"business_pipeline",'
        '"explanation":"Consulta empresarial estructurada."}'
    )
    decision = parse_reasoning_response(raw)
    assert decision.intent == "business_query"
    assert decision.recommended_route == ROUTE_BUSINESS_PIPELINE


def test_metrics_match_rate() -> None:
    reset_metrics()
    metrics = get_metrics()
    metrics.record(route_match=True)
    metrics.record(route_match=False)
    assert metrics.total_observations == 2
    assert metrics.route_matches == 1
    assert metrics.match_rate == 0.5
