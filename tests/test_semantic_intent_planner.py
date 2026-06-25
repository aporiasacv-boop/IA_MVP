from app.semantic_intent.execution_planner import build_execution_plan
from app.semantic_intent.semantic_parser import parse_semantic_question


def test_conversational_verb() -> None:
    parse = parse_semantic_question("Quien es el cliente WALMART")
    plan = build_execution_plan(parse)
    assert plan.detected_verb == "quien_es"
    assert plan.execution_strategy == "ontology_exploration"


def test_capability_discovery() -> None:
    parse = parse_semantic_question("Que sabes sobre movimientos")
    plan = build_execution_plan(parse)
    assert plan.execution_strategy == "capability_discovery"


def test_analytic_strategy() -> None:
    parse = parse_semantic_question("Analizar movimientos del proveedor en compras")
    plan = build_execution_plan(parse)
    assert plan.detected_verb == "analizar"
    assert plan.execution_strategy == "eko_full_analysis"
    assert "patterns" in plan.required_knowledge
