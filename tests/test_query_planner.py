import pytest
from fastapi.testclient import TestClient

from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation
from app.main import app
from app.query_engine.query_planner import BusinessQueryPlanner
from app.query_engine.query_types import BusinessQueryType
from app.schemas.semantic_intent import BusinessFilters, BusinessSemanticIntent
from app.services.semantic_intent_builder import SemanticIntentBuilder


@pytest.fixture
def planner() -> BusinessQueryPlanner:
    return BusinessQueryPlanner()


@pytest.fixture
def builder() -> SemanticIntentBuilder:
    return SemanticIntentBuilder()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _intent(
    operation: BusinessOperation | None = None,
    target_entity: BusinessEntity | None = None,
    source_entity: BusinessEntity | None = None,
    filters: BusinessFilters | None = None,
) -> BusinessSemanticIntent:
    return BusinessSemanticIntent(
        operation=operation,
        target_entity=target_entity,
        source_entity=source_entity,
        filters=filters or BusinessFilters(),
        source_question="pregunta de prueba",
    )


@pytest.mark.parametrize(
    ("intent", "expected_type", "expected_filters"),
    [
        (
            _intent(BusinessOperation.COUNT, BusinessEntity.CLIENTE),
            BusinessQueryType.COUNT_CLIENTES,
            {},
        ),
        (
            _intent(BusinessOperation.COUNT, BusinessEntity.PROVEEDOR),
            BusinessQueryType.COUNT_PROVEEDORES,
            {},
        ),
        (
            _intent(BusinessOperation.TOP, BusinessEntity.CLIENTE),
            BusinessQueryType.TOP_CLIENTES,
            {},
        ),
        (
            _intent(BusinessOperation.TOP, BusinessEntity.PROVEEDOR),
            BusinessQueryType.TOP_PROVEEDORES,
            {},
        ),
        (
            _intent(
                BusinessOperation.MAX,
                BusinessEntity.PROVEEDOR,
                filters=BusinessFilters(mes=6),
            ),
            BusinessQueryType.MAX_PROVEEDOR_MES,
            {"mes": 6},
        ),
        (
            _intent(BusinessOperation.MAX, BusinessEntity.PROVEEDOR),
            BusinessQueryType.MAX_PROVEEDOR_MES,
            {},
        ),
        (
            _intent(
                BusinessOperation.MAX,
                BusinessEntity.TRANSACCION,
                filters=BusinessFilters(cliente_codigo="C001"),
            ),
            BusinessQueryType.MAX_TRANSACCION_CLIENTE,
            {"cliente_codigo": "C001"},
        ),
        (
            _intent(BusinessOperation.MAX, BusinessEntity.TRANSACCION),
            BusinessQueryType.MAX_TRANSACCION_CLIENTE,
            {},
        ),
        (
            _intent(
                BusinessOperation.LOOKUP,
                BusinessEntity.CLIENTE,
                BusinessEntity.CUENTA,
            ),
            BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA,
            {},
        ),
        (
            _intent(
                BusinessOperation.LOOKUP,
                BusinessEntity.CLIENTE,
                BusinessEntity.CUENTA,
                BusinessFilters(cuenta_codigo="IMA0709183"),
            ),
            BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA,
            {"cuenta_codigo": "IMA0709183"},
        ),
        (
            _intent(BusinessOperation.SYSTEM_INFO),
            BusinessQueryType.SYSTEM_CAPABILITIES,
            {},
        ),
        (
            _intent(BusinessOperation.DATA_COVERAGE),
            BusinessQueryType.DATA_COVERAGE,
            {},
        ),
        (
            _intent(BusinessOperation.DATASET_INFO),
            BusinessQueryType.DATASET_INFO,
            {},
        ),
    ],
)
def test_plan_supported_rules(
    planner: BusinessQueryPlanner,
    intent: BusinessSemanticIntent,
    expected_type: BusinessQueryType,
    expected_filters: dict,
) -> None:
    result = planner.plan(intent)
    assert result.query_type == expected_type
    assert result.filters == expected_filters


@pytest.mark.parametrize(
    ("intent",),
    [
        (_intent(BusinessOperation.LOOKUP, BusinessEntity.CLIENTE),),
        (_intent(BusinessOperation.SUM, BusinessEntity.CLIENTE),),
        (_intent(None, BusinessEntity.CLIENTE),),
        (_intent(BusinessOperation.COUNT, None),),
    ],
)
def test_plan_unsupported_intents(
    planner: BusinessQueryPlanner,
    intent: BusinessSemanticIntent,
) -> None:
    result = planner.plan(intent)
    assert result.query_type == BusinessQueryType.UNSUPPORTED


def test_plan_count_clientes_from_question(builder: SemanticIntentBuilder, planner: BusinessQueryPlanner) -> None:
    intent = builder.build("¿Cuántos clientes existen?")
    result = planner.plan(intent)
    assert result.query_type == BusinessQueryType.COUNT_CLIENTES
    assert result.filters == {}


def test_plan_max_proveedor_mes_from_question(
    builder: SemanticIntentBuilder,
    planner: BusinessQueryPlanner,
) -> None:
    intent = builder.build("¿Qué proveedor tuvo más movimiento en junio?")
    result = planner.plan(intent)
    assert result.query_type == BusinessQueryType.MAX_PROVEEDOR_MES
    assert result.filters["mes"] == 6


def test_plan_max_transaccion_cliente_from_question(
    builder: SemanticIntentBuilder,
    planner: BusinessQueryPlanner,
) -> None:
    intent = builder.build("¿Cuál fue la transacción más alta del cliente C001?")
    result = planner.plan(intent)
    assert result.query_type == BusinessQueryType.MAX_TRANSACCION_CLIENTE
    assert result.filters["cliente_codigo"] == "C001"


def test_plan_lookup_cliente_by_cuenta_from_question(
    builder: SemanticIntentBuilder,
    planner: BusinessQueryPlanner,
) -> None:
    intent = builder.build("¿De qué cliente es la cuenta IMA0709183?")
    result = planner.plan(intent)
    assert result.query_type == BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA
    assert result.filters["cuenta_codigo"] == "IMA0709183"


def test_plan_unsupported_from_question(builder: SemanticIntentBuilder, planner: BusinessQueryPlanner) -> None:
    intent = builder.build("¿Cuál fue la actividad de proveedores en 2025?")
    result = planner.plan(intent)
    assert result.query_type == BusinessQueryType.UNSUPPORTED
    assert result.filters["anio"] == 2025


def test_query_plan_endpoint_count_clientes(client: TestClient) -> None:
    response = client.get(
        "/api/query/plan",
        params={"question": "¿Cuántos clientes existen?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "COUNT_CLIENTES"
    assert data["filters"] == {}


def test_query_plan_endpoint_max_proveedor_mes(client: TestClient) -> None:
    response = client.get(
        "/api/query/plan",
        params={"question": "¿Qué proveedor tuvo más movimiento en junio?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "MAX_PROVEEDOR_MES"
    assert data["filters"]["mes"] == 6


def test_query_plan_endpoint_max_transaccion_cliente(client: TestClient) -> None:
    response = client.get(
        "/api/query/plan",
        params={"question": "¿Cuál fue la transacción más alta del cliente C001?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "MAX_TRANSACCION_CLIENTE"
    assert data["filters"]["cliente_codigo"] == "C001"


def test_query_plan_endpoint_lookup_cliente_by_cuenta(client: TestClient) -> None:
    response = client.get(
        "/api/query/plan",
        params={"question": "¿De qué cliente es la cuenta IMA0709183?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "LOOKUP_CLIENTE_BY_CUENTA"
    assert data["filters"]["cuenta_codigo"] == "IMA0709183"


def test_query_plan_endpoint_requires_question(client: TestClient) -> None:
    response = client.get("/api/query/plan")
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("question", "expected_type"),
    [
        ("¿Qué datos tienes?", "DATASET_INFO"),
        ("¿Qué puedo preguntarte?", "SYSTEM_CAPABILITIES"),
        ("¿Cuál es el periodo de los datos?", "DATA_COVERAGE"),
        ("¿Qué fechas cubren los datos?", "DATA_COVERAGE"),
        ("¿Cuántos datos tienes?", "DATASET_INFO"),
        ("¿Cuántos registros tienes?", "DATASET_INFO"),
    ],
)
def test_plan_system_capability_questions_from_question(
    builder: SemanticIntentBuilder,
    planner: BusinessQueryPlanner,
    question: str,
    expected_type: str,
) -> None:
    intent = builder.build(question)
    result = planner.plan(intent)
    assert result.query_type.value == expected_type
    assert intent.operation is not None


@pytest.mark.parametrize(
    ("question", "expected_type"),
    [
        ("¿Qué datos tienes?", "DATASET_INFO"),
        ("¿Qué puedo preguntarte?", "SYSTEM_CAPABILITIES"),
        ("¿Cuál es el periodo de los datos?", "DATA_COVERAGE"),
        ("¿Qué fechas cubren los datos?", "DATA_COVERAGE"),
        ("¿Cuántos datos tienes?", "DATASET_INFO"),
        ("¿Cuántos registros tienes?", "DATASET_INFO"),
    ],
)
def test_query_plan_endpoint_system_capability_questions(
    client: TestClient,
    question: str,
    expected_type: str,
) -> None:
    response = client.get("/api/query/plan", params={"question": question})
    assert response.status_code == 200
    assert response.json()["query_type"] == expected_type
