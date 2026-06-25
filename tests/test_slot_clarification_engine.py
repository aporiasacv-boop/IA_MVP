import pytest

from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.schemas.semantic_intent import BusinessFilters, BusinessSemanticIntent
from app.slot_clarification.engine import SlotClarificationEngine


@pytest.fixture
def engine() -> SlotClarificationEngine:
    return SlotClarificationEngine()


def _intent(
    *,
    operation: BusinessOperation | None = None,
    target_entity: BusinessEntity | None = None,
    source_entity: BusinessEntity | None = None,
    filters: BusinessFilters | None = None,
    confidence: float = 0.9,
) -> BusinessSemanticIntent:
    return BusinessSemanticIntent(
        operation=operation,
        target_entity=target_entity,
        source_entity=source_entity,
        filters=filters or BusinessFilters(),
        confidence=confidence,
        source_question="pregunta de prueba",
    )


def test_resolve_max_transaccion_cliente_without_cliente_codigo(
    engine: SlotClarificationEngine,
) -> None:
    intent = _intent(
        operation=BusinessOperation.MAX,
        target_entity=BusinessEntity.TRANSACCION,
    )
    query = BusinessQuery(query_type=BusinessQueryType.MAX_TRANSACCION_CLIENTE)

    result = engine.resolve(intent, query)

    assert result is not None
    assert result.success is True
    assert result.pending_query_type == "MAX_TRANSACCION_CLIENTE"
    assert result.missing_slots == ["cliente_codigo"]
    assert result.answer == "¿De qué cliente deseas consultar la información?"
    assert result.session_token


def test_resolve_max_proveedor_mes_without_mes(engine: SlotClarificationEngine) -> None:
    intent = _intent(
        operation=BusinessOperation.MAX,
        target_entity=BusinessEntity.PROVEEDOR,
    )
    query = BusinessQuery(query_type=BusinessQueryType.MAX_PROVEEDOR_MES)

    result = engine.resolve(intent, query)

    assert result is not None
    assert result.pending_query_type == "MAX_PROVEEDOR_MES"
    assert result.missing_slots == ["mes"]
    assert result.answer == "¿De qué mes deseas realizar la consulta?"


def test_resolve_lookup_cliente_by_cuenta_without_cuenta_codigo(
    engine: SlotClarificationEngine,
) -> None:
    intent = _intent(
        operation=BusinessOperation.LOOKUP,
        target_entity=BusinessEntity.CLIENTE,
        source_entity=BusinessEntity.CUENTA,
    )
    query = BusinessQuery(query_type=BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA)

    result = engine.resolve(intent, query)

    assert result is not None
    assert result.pending_query_type == "LOOKUP_CLIENTE_BY_CUENTA"
    assert result.missing_slots == ["cuenta_codigo"]
    assert result.answer == "¿Cuál es el código de cuenta?"


def test_resolve_count_clientes_without_clarification(
    engine: SlotClarificationEngine,
) -> None:
    intent = _intent(
        operation=BusinessOperation.COUNT,
        target_entity=BusinessEntity.CLIENTE,
    )
    query = BusinessQuery(query_type=BusinessQueryType.COUNT_CLIENTES)

    result = engine.resolve(intent, query)

    assert result is None


def test_resolve_returns_none_when_required_slots_present(
    engine: SlotClarificationEngine,
) -> None:
    intent = _intent(
        operation=BusinessOperation.MAX,
        target_entity=BusinessEntity.TRANSACCION,
        filters=BusinessFilters(cliente_codigo="C001"),
    )
    query = BusinessQuery(
        query_type=BusinessQueryType.MAX_TRANSACCION_CLIENTE,
        filters={"cliente_codigo": "C001"},
    )

    result = engine.resolve(intent, query)

    assert result is None
