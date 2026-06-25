import pytest

from app.query_engine.query_types import BusinessQueryType
from app.suggested_questions.engine import SuggestedQuestionsEngine
from app.suggested_questions.rules import TYPE_SPECIFIC_RULES
from app.suggested_questions.validator import validate_questions


@pytest.fixture
def engine() -> SuggestedQuestionsEngine:
    return SuggestedQuestionsEngine(
        top_questions_provider=lambda limit: [
            "¿Cuántos clientes existen?",
            "¿Qué proveedor tuvo más movimiento en junio?",
            "¿Cuál es el periodo de los datos?",
        ][:limit],
    )


def test_generate_count_clientes_uses_type_rules(engine: SuggestedQuestionsEngine) -> None:
    result = engine.generate(current_query_type=BusinessQueryType.COUNT_CLIENTES.value)

    assert 3 <= len(result.questions) <= 4
    assert result.source in {"type_rules", "mixed"}
    for rule_question in TYPE_SPECIFIC_RULES[BusinessQueryType.COUNT_CLIENTES]:
        if rule_question in validate_questions([rule_question]):
            assert rule_question in result.questions


def test_generate_top_clientes_suggests_related_queries(engine: SuggestedQuestionsEngine) -> None:
    result = engine.generate(current_query_type=BusinessQueryType.TOP_CLIENTES.value)

    assert 3 <= len(result.questions) <= 4
    assert any(
        "proveedor" in question.lower() or "cliente" in question.lower()
        for question in result.questions
    )


def test_generate_max_proveedor_mes_suggests_follow_ups(engine: SuggestedQuestionsEngine) -> None:
    result = engine.generate(current_query_type=BusinessQueryType.MAX_PROVEEDOR_MES.value)

    assert 3 <= len(result.questions) <= 4
    assert len(result.questions) == len(set(q.lower() for q in result.questions))


def test_generate_capability_discovery_context(engine: SuggestedQuestionsEngine) -> None:
    result = engine.generate(
        current_query_type="capability_discovery",
        handled_by="capability_discovery",
    )

    assert 3 <= len(result.questions) <= 4
    assert result.metadata["handled_by"] == "capability_discovery"


def test_generate_guided_fallback_context(engine: SuggestedQuestionsEngine) -> None:
    result = engine.generate(
        current_query_type="UNKNOWN",
        handled_by="guided_fallback",
    )

    assert 3 <= len(result.questions) <= 4
    assert result.metadata["handled_by"] == "guided_fallback"


def test_generate_never_exceeds_four_questions(engine: SuggestedQuestionsEngine) -> None:
    result = engine.generate(
        current_query_type=BusinessQueryType.COUNT_CLIENTES.value,
    )
    assert len(result.questions) <= 4


def test_validate_questions_filters_blocked_suggestions() -> None:
    validated = validate_questions([
        "¿Cuántos clientes existen?",
        "¿Puedes hacer predicciones?",
        "¿Puedes comparar meses?",
    ])
    assert "¿Cuántos clientes existen?" in validated
    assert "¿Puedes hacer predicciones?" not in validated
    assert "¿Puedes comparar meses?" not in validated


def test_generate_product_identity_skips_type_rules(engine: SuggestedQuestionsEngine) -> None:
    result = engine.generate(handled_by="product_identity")
    assert 3 <= len(result.questions) <= 4
    assert result.metadata["handled_by"] == "product_identity"


def test_validate_questions_filters_unsupported() -> None:
    validated = validate_questions([
        "¿Cuántos clientes existen?",
        "¿Cómo evolucionó ese cliente?",
        "¿Cuál es el segundo cliente?",
    ])
    assert "¿Cuántos clientes existen?" in validated
    assert "¿Cómo evolucionó ese cliente?" not in validated


def test_generate_uses_confidence_when_provided(engine: SuggestedQuestionsEngine) -> None:
    result = engine.generate(
        current_query_type=BusinessQueryType.COUNT_CLIENTES.value,
        confidence=0.95,
    )
    assert result.confidence == 0.95


def test_generate_without_query_type_uses_defaults(engine: SuggestedQuestionsEngine) -> None:
    result = engine.generate(current_query_type=None)
    assert 3 <= len(result.questions) <= 4


def test_generate_questions_are_planner_supported(engine: SuggestedQuestionsEngine) -> None:
    from app.query_engine.query_planner import BusinessQueryPlanner
    from app.services.semantic_intent_builder import SemanticIntentBuilder

    planner = BusinessQueryPlanner()
    intent_builder = SemanticIntentBuilder()
    result = engine.generate(current_query_type=BusinessQueryType.COUNT_CLIENTES.value)

    for question in result.questions:
        intent = intent_builder.build(question)
        query = planner.plan(intent)
        assert query.query_type != BusinessQueryType.UNSUPPORTED, question
