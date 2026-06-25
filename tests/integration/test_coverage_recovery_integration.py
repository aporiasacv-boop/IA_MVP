import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.coverage_recovery.patterns import (
    CAPABILITY_DISCOVERY_QUERIES,
    DATA_COVERAGE_QUERIES,
    DATASET_INFO_QUERIES,
    REGRESSION_BUSINESS_QUERIES,
)
from app.database.database import SessionLocal
from app.main import app


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def recovery_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    return TestClient(app)


@pytest.mark.parametrize("question", DATA_COVERAGE_QUERIES)
def test_integration_data_coverage_queries(recovery_client: TestClient, question: str) -> None:
    response = recovery_client.post("/api/chat/hybrid", json={"message": question})
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "business_pipeline"
    assert data["metadata"]["query_type"] == "DATA_COVERAGE"
    assert data["handled_by"] != "guided_fallback"


@pytest.mark.parametrize("question", DATASET_INFO_QUERIES)
def test_integration_dataset_info_queries(recovery_client: TestClient, question: str) -> None:
    response = recovery_client.post("/api/chat/hybrid", json={"message": question})
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "business_pipeline"
    assert data["metadata"]["query_type"] == "DATASET_INFO"
    assert data["handled_by"] != "guided_fallback"


@pytest.mark.parametrize("question", CAPABILITY_DISCOVERY_QUERIES)
def test_integration_capability_discovery_queries(
    recovery_client: TestClient,
    question: str,
) -> None:
    response = recovery_client.post("/api/chat/hybrid", json={"message": question})
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "capability_discovery"
    assert data["handled_by"] != "guided_fallback"


@pytest.mark.parametrize(
    ("question", "expected_query_type"),
    [
        ("¿Cuántos clientes existen?", "COUNT_CLIENTES"),
        ("¿Cuántos proveedores existen?", "COUNT_PROVEEDORES"),
        ("¿Qué proveedor tuvo más movimiento?", "MAX_PROVEEDOR_MES"),
        ("¿Cuál fue la transacción más alta?", "MAX_TRANSACCION_CLIENTE"),
        ("Muéstrame los principales clientes", "TOP_CLIENTES"),
    ],
)
def test_integration_regression_business_queries(
    recovery_client: TestClient,
    question: str,
    expected_query_type: str,
) -> None:
    response = recovery_client.post("/api/chat/hybrid", json={"message": question})
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] in {"business_pipeline", "slot_clarification"}
    if data["handled_by"] == "business_pipeline":
        assert data["metadata"]["query_type"] == expected_query_type
    else:
        assert data["metadata"]["pending_query_type"] == expected_query_type


def test_integration_coverage_recovery_metrics_in_response(recovery_client: TestClient) -> None:
    response = recovery_client.post(
        "/api/chat/hybrid",
        json={"message": DATA_COVERAGE_QUERIES[0]},
    )
    assert response.status_code == 200
    metadata = response.json()["metadata"]
    assert "coverage_recovery_hits" in metadata
    assert "coverage_recovery_misses" in metadata
