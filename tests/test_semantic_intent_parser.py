from app.semantic_intent.execution_planner import build_execution_plan
from app.semantic_intent.semantic_parser import parse_semantic_question


def test_parse_listar_clientes() -> None:
    result = parse_semantic_question("Listar los principales clientes este mes")
    assert result.business_verb is not None
    assert result.business_verb.verb_id == "listar"
    assert any(obj.object_id == "cliente" for obj in result.business_objects)
    assert "este mes" in result.business_time


def test_parse_evaluar_riesgo() -> None:
    result = parse_semantic_question("Evaluar riesgos de la entidad WALMART")
    assert result.business_verb is not None
    assert result.business_verb.verb_id == "evaluar"
    assert any(obj.object_id in {"riesgo", "entidad"} for obj in result.business_objects)


def test_parse_unknown_verb() -> None:
    result = parse_semantic_question("xyzabc movimientos")
    assert result.business_verb is None
    assert "verb" in result.unknown_tokens


def test_plan_executive_question() -> None:
    parse = parse_semantic_question("Recomendar acciones para clientes con alto volumen")
    plan = build_execution_plan(parse)
    assert plan.detected_verb == "recomendar"
    assert "recommendations" in plan.required_reasoning
    assert plan.execution_strategy == "ero_recommendation_review"


def test_plan_informative_question() -> None:
    parse = parse_semantic_question("Mostrar perfil del cliente")
    plan = build_execution_plan(parse)
    assert plan.detected_verb == "mostrar"
    assert "identity" in plan.required_knowledge
    assert plan.execution_strategy in {"eko_profile_summary", "eko_identity_lookup"}
