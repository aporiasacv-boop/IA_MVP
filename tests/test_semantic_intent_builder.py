import pytest
from fastapi.testclient import TestClient

from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation
from app.main import app
from app.services.semantic_intent_builder import SemanticIntentBuilder


@pytest.fixture
def builder() -> SemanticIntentBuilder:
    return SemanticIntentBuilder()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_build_count_clientes(builder: SemanticIntentBuilder) -> None:
    result = builder.build("¿Cuántos clientes existen?")
    assert result.operation == BusinessOperation.COUNT
    assert result.target_entity == BusinessEntity.CLIENTE
    assert result.source_entity is None
    assert result.confidence > 0


def test_build_max_proveedor_junio(builder: SemanticIntentBuilder) -> None:
    result = builder.build("¿Qué proveedor tuvo más movimiento en junio?")
    assert result.operation == BusinessOperation.MAX
    assert result.target_entity == BusinessEntity.PROVEEDOR
    assert result.source_entity is None
    assert result.filters.mes == 6
    assert result.confidence > 0


def test_build_max_transaccion_cliente_codigo(builder: SemanticIntentBuilder) -> None:
    result = builder.build("¿Cuál fue la transacción más alta del cliente C001?")
    assert result.operation == BusinessOperation.MAX
    assert result.target_entity == BusinessEntity.TRANSACCION
    assert result.source_entity == BusinessEntity.CLIENTE
    assert result.filters.cliente_codigo == "C001"
    assert result.confidence > 0


def test_build_lookup_cliente_cuenta(builder: SemanticIntentBuilder) -> None:
    result = builder.build("¿De qué cliente es la cuenta IMA0709183?")
    assert result.operation == BusinessOperation.LOOKUP
    assert result.target_entity == BusinessEntity.CLIENTE
    assert result.source_entity == BusinessEntity.CUENTA
    assert result.filters.cuenta_codigo == "IMA0709183"
    assert result.confidence > 0


def test_build_proveedor_anio(builder: SemanticIntentBuilder) -> None:
    result = builder.build("¿Cuál fue la actividad de proveedores en 2025?")
    assert result.target_entity == BusinessEntity.PROVEEDOR
    assert result.filters.anio == 2025
    assert result.confidence > 0


def test_build_without_matches(builder: SemanticIntentBuilder) -> None:
    result = builder.build("Hola buenos dias")
    assert result.operation is None
    assert result.target_entity is None
    assert result.source_entity is None
    assert result.confidence == 0.0


def test_semantic_intent_endpoint(client: TestClient) -> None:
    response = client.get(
        "/api/semantic/intent",
        params={"question": "¿Cuál fue la transacción más alta del cliente C001?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "MAX"
    assert data["target_entity"] == "TRANSACCION"
    assert data["source_entity"] == "CLIENTE"
    assert data["filters"]["cliente_codigo"] == "C001"
    assert data["confidence"] > 0
    assert data["source_question"]


def test_semantic_intent_endpoint_requires_question(client: TestClient) -> None:
    response = client.get("/api/semantic/intent")
    assert response.status_code == 422
