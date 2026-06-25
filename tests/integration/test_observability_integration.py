import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.database import SessionLocal
from app.main import app
from app.observability.metrics_repository import PerformanceMetricsRepository


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def integration_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        session.execute(text("SELECT 1 FROM performance_metrics LIMIT 1"))
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL o tabla performance_metrics no disponible: {exc}")
    session.close()
    return TestClient(app)


def test_integration_hybrid_chat_persists_metrics(integration_client: TestClient) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Cuántos clientes existen?"},
    )
    assert response.status_code == 200
    assert response.json()["handled_by"] == "business_pipeline"

    session = SessionLocal()
    try:
        repository = PerformanceMetricsRepository(session)
        assert repository.count_all() >= 1
        summary = repository.get_summary()
        assert summary["total_requests"] >= 1
    finally:
        session.close()


def test_integration_metrics_endpoints_after_hybrid_request(
    integration_client: TestClient,
) -> None:
    integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Cuántos proveedores existen?"},
    )

    summary = integration_client.get("/api/metrics/summary")
    assert summary.status_code == 200
    assert summary.json()["total_requests"] >= 1

    top_queries = integration_client.get("/api/metrics/top-queries")
    assert top_queries.status_code == 200
    assert isinstance(top_queries.json(), list)

    performance = integration_client.get("/api/metrics/performance")
    assert performance.status_code == 200
    data = performance.json()
    assert "p50_total_time_ms" in data
    assert "averages" in data
