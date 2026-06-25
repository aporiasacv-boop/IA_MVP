import pytest
from fastapi.testclient import TestClient

from app.domain.entities import BusinessEntity
from app.main import app
from app.services.entity_resolver import EntityResolver


@pytest.fixture
def resolver() -> EntityResolver:
    return EntityResolver()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_resolve_clientes_existen(resolver: EntityResolver) -> None:
    result = resolver.resolve("¿Cuántos clientes existen?")
    assert result.entities == [BusinessEntity.CLIENTE]
    assert result.parameters == {}
    assert result.confidence == 1.0
    assert result.matched_terms


def test_resolve_proveedor_movimiento_junio(resolver: EntityResolver) -> None:
    result = resolver.resolve("¿Qué proveedor tuvo más movimiento en junio?")
    assert set(result.entities) == {BusinessEntity.PROVEEDOR, BusinessEntity.MOVIMIENTO}
    assert result.parameters["mes"] == "junio"
    assert BusinessEntity.MES not in result.entities
    assert result.confidence > 0


def test_resolve_cliente_cuenta_codigo(resolver: EntityResolver) -> None:
    result = resolver.resolve("¿De qué cliente es la cuenta IMA0709183?")
    assert set(result.entities) == {BusinessEntity.CLIENTE, BusinessEntity.CUENTA}
    assert result.parameters["codigo"] == "IMA0709183"
    assert result.confidence > 0


def test_resolve_transaccion_cliente_codigo(resolver: EntityResolver) -> None:
    result = resolver.resolve("¿Cuál fue la transacción más alta del cliente C001?")
    assert set(result.entities) == {BusinessEntity.TRANSACCION, BusinessEntity.CLIENTE}
    assert result.parameters["codigo"] == "C001"
    assert result.confidence > 0


def test_resolve_proveedor_anio(resolver: EntityResolver) -> None:
    result = resolver.resolve("¿Cuál fue la actividad de proveedores en 2025?")
    assert set(result.entities) == {BusinessEntity.PROVEEDOR, BusinessEntity.ANIO}
    assert result.parameters["anio"] == 2025
    assert result.confidence > 0


def test_resolve_without_matches_returns_empty(resolver: EntityResolver) -> None:
    result = resolver.resolve("Hola buenos dias")
    assert result.entities == []
    assert result.parameters == {}
    assert result.confidence == 0.0
    assert result.matched_terms == []


def test_semantic_entity_endpoint(client: TestClient) -> None:
    response = client.get(
        "/api/semantic/entity",
        params={"question": "¿De qué cliente es la cuenta IMA0709183?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert set(data["entities"]) == {"CLIENTE", "CUENTA"}
    assert data["parameters"]["codigo"] == "IMA0709183"
    assert data["confidence"] > 0
    assert data["matched_terms"]


def test_semantic_entity_endpoint_requires_question(client: TestClient) -> None:
    response = client.get("/api/semantic/entity")
    assert response.status_code == 422
