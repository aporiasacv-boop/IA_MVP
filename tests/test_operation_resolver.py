import pytest
from fastapi.testclient import TestClient

from app.domain.operations import BusinessOperation
from app.main import app
from app.services.operation_resolver import OperationResolver


@pytest.fixture
def resolver() -> OperationResolver:
    return OperationResolver()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    ("question", "expected_operation"),
    [
        ("¿Cuántos clientes existen?", BusinessOperation.COUNT),
        ("¿Qué proveedor tuvo mayor movimiento?", BusinessOperation.MAX),
        ("Muéstrame los principales clientes", BusinessOperation.TOP),
        ("¿Cuál es el volumen total?", BusinessOperation.SUM),
        ("¿Cuál es el promedio mensual?", BusinessOperation.AVG),
        ("¿Qué datos tienes?", BusinessOperation.DATASET_INFO),
        ("¿Qué puedo preguntarte?", BusinessOperation.SYSTEM_INFO),
        ("¿Cuál es el periodo de los datos?", BusinessOperation.DATA_COVERAGE),
        ("¿Cuántos datos tienes?", BusinessOperation.DATASET_INFO),
        ("¿Cuántos registros tienes?", BusinessOperation.DATASET_INFO),
    ],
)
def test_resolve_required_cases(
    resolver: OperationResolver,
    question: str,
    expected_operation: BusinessOperation,
) -> None:
    result = resolver.resolve(question)
    assert result.operation == expected_operation
    assert result.confidence > 0
    assert result.matched_terms


def test_resolve_without_matches_returns_none(resolver: OperationResolver) -> None:
    result = resolver.resolve("Hola buenos dias")
    assert result.operation is None
    assert result.confidence == 0.0
    assert result.matched_terms == []


def test_semantic_operation_endpoint(client: TestClient) -> None:
    response = client.get(
        "/api/semantic/operation",
        params={"question": "¿Cuántos clientes existen?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "COUNT"
    assert data["confidence"] == 1.0
    assert "cuantos" in data["matched_terms"] or "cuántos" in data["matched_terms"]
    assert "existen" in data["matched_terms"]


def test_semantic_operation_endpoint_requires_question(client: TestClient) -> None:
    response = client.get("/api/semantic/operation")
    assert response.status_code == 422
