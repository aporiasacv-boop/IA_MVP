import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.database.database import SessionLocal, engine
from app.enterprise_reasoning.metrics import EnterpriseReasoningMetrics
from app.main import app
from app.models.enterprise_reasoning_object import EnterpriseReasoningObject


pytestmark = pytest.mark.integration


def _ensure_tables() -> None:
    inspector = inspect(engine)
    names = set(inspector.get_table_names())
    if EnterpriseReasoningObject.__tablename__ not in names:
        EnterpriseReasoningObject.__table__.create(bind=engine)


@pytest.fixture(scope="module")
def reasoning_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        _ensure_tables()
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    EnterpriseReasoningMetrics.reset_for_tests()
    return TestClient(app)


def test_integration_reasoning_list(reasoning_client: TestClient) -> None:
    response = reasoning_client.get("/api/reasoning/entities?page=1&page_size=5")
    assert response.status_code == 200


def test_integration_reasoning_rules(reasoning_client: TestClient) -> None:
    response = reasoning_client.get("/api/reasoning/rules")
    assert response.status_code == 200
    assert response.json()["total_rules"] >= 10


def test_integration_reasoning_statistics(reasoning_client: TestClient) -> None:
    response = reasoning_client.get("/api/reasoning/statistics")
    assert response.status_code == 200
    assert "reasoning_objects_total" in response.json()


def test_integration_metrics_reasoning_fields(reasoning_client: TestClient) -> None:
    response = reasoning_client.get("/api/metrics/summary")
    assert response.status_code == 200
    assert "reasoning_objects_total" in response.json()
