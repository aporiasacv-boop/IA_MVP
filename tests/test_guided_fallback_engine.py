import pytest

from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation
from app.guided_fallback.classifier import (
    classify_fallback_type,
    should_delegate_to_legacy,
)
from app.guided_fallback.engine import GuidedFallbackEngine
from app.guided_fallback.suggested_questions import build_suggested_questions
from app.guided_fallback.templates import (
    AMBIGUOUS_FOOTER,
    OUT_OF_DOMAIN_ANSWER,
    UNKNOWN_CAPABILITIES,
    UNKNOWN_HEADER,
)
from app.guided_fallback.types import FallbackType
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.schemas.semantic_intent import BusinessFilters, BusinessSemanticIntent


def _unsupported_intent(
    *,
    confidence: float = 0.2,
    operation: BusinessOperation | None = None,
    target_entity: BusinessEntity | None = None,
) -> BusinessSemanticIntent:
    return BusinessSemanticIntent(
        operation=operation,
        target_entity=target_entity,
        source_entity=None,
        filters=BusinessFilters(),
        confidence=confidence,
        source_question="",
    )


def _unsupported_query() -> BusinessQuery:
    return BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED, filters={})


@pytest.fixture
def engine() -> GuidedFallbackEngine:
    return GuidedFallbackEngine(
        top_questions_provider=lambda limit: [
            "¿Cuántos clientes existen?",
            "¿Cuántos proveedores existen?",
            "¿Qué proveedor tuvo más movimiento en junio?",
        ][:limit],
    )


def test_classify_unknown_discovery_question() -> None:
    intent = _unsupported_intent()
    result = classify_fallback_type(
        "hola equipo de datos",
        intent,
        _unsupported_query(),
        None,
    )
    assert result == FallbackType.UNKNOWN


def test_classify_ambiguous_question() -> None:
    intent = _unsupported_intent()
    result = classify_fallback_type(
        "¿Cómo va el negocio?",
        intent,
        _unsupported_query(),
        None,
    )
    assert result == FallbackType.AMBIGUOUS


def test_classify_out_of_domain_question() -> None:
    intent = _unsupported_intent()
    result = classify_fallback_type(
        "¿Quién ganó el mundial?",
        intent,
        _unsupported_query(),
        None,
    )
    assert result == FallbackType.OUT_OF_DOMAIN


def test_classify_low_confidence_partial_intent() -> None:
    intent = _unsupported_intent(
        confidence=0.3,
        operation=BusinessOperation.COUNT,
        target_entity=BusinessEntity.CLIENTE,
    )
    result = classify_fallback_type(
        "clientes del sector salud",
        intent,
        _unsupported_query(),
        None,
    )
    assert result == FallbackType.LOW_CONFIDENCE


def test_classify_unsupported_capability_partial_intent() -> None:
    intent = _unsupported_intent(
        confidence=0.8,
        operation=BusinessOperation.COUNT,
        target_entity=BusinessEntity.CLIENTE,
    )
    result = classify_fallback_type(
        "clientes por región",
        intent,
        _unsupported_query(),
        None,
    )
    assert result == FallbackType.UNSUPPORTED_CAPABILITY


def test_classify_returns_none_for_supported_query() -> None:
    intent = _unsupported_intent()
    query = BusinessQuery(query_type=BusinessQueryType.COUNT_CLIENTES, filters={})
    result = classify_fallback_type("¿Cuántos clientes?", intent, query, None)
    assert result is None


def test_classify_returns_none_for_legacy_delegation() -> None:
    intent = _unsupported_intent()
    result = classify_fallback_type(
        "¿Qué es un proveedor?",
        intent,
        _unsupported_query(),
        None,
    )
    assert result is None
    assert should_delegate_to_legacy("¿Qué es un proveedor?") is True


def test_resolve_unknown_includes_capabilities(engine: GuidedFallbackEngine) -> None:
    intent = _unsupported_intent()
    result = engine.resolve(
        "hola equipo de datos",
        intent,
        _unsupported_query(),
        None,
    )
    assert result is not None
    assert result.success is True
    assert result.fallback_type == FallbackType.UNKNOWN.value
    assert UNKNOWN_HEADER in result.answer
    for capability in UNKNOWN_CAPABILITIES:
        assert capability in result.answer
    assert 3 <= len(result.suggested_questions) <= 5
    assert result.metadata["fallback_success"] is True


def test_resolve_ambiguous_includes_options_and_footer(
    engine: GuidedFallbackEngine,
) -> None:
    intent = _unsupported_intent()
    result = engine.resolve(
        "¿Cómo va el negocio?",
        intent,
        _unsupported_query(),
        None,
    )
    assert result is not None
    assert result.fallback_type == FallbackType.AMBIGUOUS.value
    assert "KPIs ejecutivos" in result.answer
    assert AMBIGUOUS_FOOTER in result.answer


def test_resolve_out_of_domain_answer(engine: GuidedFallbackEngine) -> None:
    intent = _unsupported_intent()
    result = engine.resolve(
        "¿Quién ganó el mundial?",
        intent,
        _unsupported_query(),
        None,
    )
    assert result is not None
    assert result.fallback_type == FallbackType.OUT_OF_DOMAIN.value
    assert result.answer == OUT_OF_DOMAIN_ANSWER


def test_resolve_low_confidence_suggests_questions(engine: GuidedFallbackEngine) -> None:
    intent = _unsupported_intent(
        confidence=0.3,
        operation=BusinessOperation.TOP,
        target_entity=BusinessEntity.PROVEEDOR,
    )
    result = engine.resolve(
        "ranking raro",
        intent,
        _unsupported_query(),
        None,
    )
    assert result is not None
    assert result.fallback_type == FallbackType.LOW_CONFIDENCE.value
    assert len(result.suggested_questions) >= 3
    assert result.suggested_questions[0] in result.answer


def test_resolve_unsupported_capability_suggests_questions(
    engine: GuidedFallbackEngine,
) -> None:
    intent = _unsupported_intent(
        confidence=0.85,
        operation=BusinessOperation.COUNT,
        target_entity=BusinessEntity.CLIENTE,
    )
    result = engine.resolve(
        "clientes por zona",
        intent,
        _unsupported_query(),
        None,
    )
    assert result is not None
    assert result.fallback_type == FallbackType.UNSUPPORTED_CAPABILITY.value
    assert len(result.suggested_questions) >= 3


def test_resolve_returns_none_for_legacy_delegation(
    engine: GuidedFallbackEngine,
) -> None:
    intent = _unsupported_intent()
    result = engine.resolve(
        "Explícame qué observas en estos datos.",
        intent,
        _unsupported_query(),
        None,
    )
    assert result is None


def test_classify_default_unknown_without_discovery_pattern() -> None:
    intent = _unsupported_intent()
    result = classify_fallback_type(
        "hola equipo",
        intent,
        _unsupported_query(),
        None,
    )
    assert result == FallbackType.UNKNOWN


def test_build_suggested_questions_falls_back_to_capabilities_and_query_types() -> None:
    suggestions = build_suggested_questions(
        top_questions_provider=lambda limit: [],
        min_count=3,
        max_count=5,
    )
    assert len(suggestions) >= 3
    assert all(isinstance(question, str) for question in suggestions)


def test_build_suggested_questions_fills_from_defaults_when_sparse() -> None:
    suggestions = build_suggested_questions(
        top_questions_provider=lambda limit: ["Solo una pregunta"],
        min_count=3,
        max_count=5,
    )
    assert len(suggestions) >= 3
    assert suggestions[0] == "Solo una pregunta"


def test_build_suggested_questions_uses_query_type_examples_when_needed() -> None:
    suggestions = build_suggested_questions(
        top_questions_provider=lambda limit: ["Pregunta personalizada"],
        min_count=3,
        max_count=12,
    )
    assert len(suggestions) >= 9
    assert suggestions[0] == "Pregunta personalizada"


def test_build_suggested_questions_exhausts_available_catalog() -> None:
    suggestions = build_suggested_questions(
        top_questions_provider=lambda limit: [],
        min_count=20,
        max_count=20,
    )
    assert len(suggestions) == 11


def test_build_suggested_questions_uses_top_queries_first() -> None:
    seen: list[int] = []

    def provider(limit: int) -> list[str]:
        seen.append(limit)
        return ["Pregunta top 1", "Pregunta top 2", "Pregunta top 3"]

    suggestions = build_suggested_questions(top_questions_provider=provider)
    assert suggestions[:3] == [
        "Pregunta top 1",
        "Pregunta top 2",
        "Pregunta top 3",
    ]
    assert seen == [5]
