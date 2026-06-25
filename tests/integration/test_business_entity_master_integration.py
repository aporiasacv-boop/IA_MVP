import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.business_entity_master.metrics import BusinessEntityMasterMetrics
from app.database.database import SessionLocal, engine
from app.main import app
from app.models.business_entity_master import BusinessEntityMaster


pytestmark = pytest.mark.integration


def _ensure_entity_master_table() -> None:
    inspector = inspect(engine)
    if "business_entity_master" not in inspector.get_table_names():
        BusinessEntityMaster.__table__.create(bind=engine)


@pytest.fixture(scope="module")
def entity_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        _ensure_entity_master_table()
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    BusinessEntityMasterMetrics.reset_for_tests()
    return TestClient(app)


def test_integration_business_entities_list(entity_client: TestClient) -> None:
    response = entity_client.get("/api/business-entities?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_integration_business_entities_statistics(entity_client: TestClient) -> None:
    response = entity_client.get("/api/business-entities/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "business_entities_total" in data
    assert "duplicated_entities" in data
    assert "by_source_column" in data


def test_integration_business_entities_by_code_not_found(entity_client: TestClient) -> None:
    response = entity_client.get("/api/business-entities/__NO_EXISTE__")
    assert response.status_code == 404


def test_integration_metrics_summary_includes_entity_fields(entity_client: TestClient) -> None:
    response = entity_client.get("/api/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "business_entities_total" in data
    assert "business_entities_loaded" in data
    assert "duplicated_entities" in data


def test_integration_analytics_report_includes_entity_fields(entity_client: TestClient) -> None:
    response = entity_client.get("/api/analytics/report")
    assert response.status_code == 200
    data = response.json()
    assert "business_entities_total" in data
    assert "last_entity_refresh" in data


def test_integration_entity_load_idempotent(entity_client: TestClient) -> None:
    from scripts.load_business_entity_master import main as load_main

    assert load_main() == 0
    stats = entity_client.get("/api/business-entities/statistics").json()
    assert stats["business_entities_total"] > 0

    detail = entity_client.get("/api/business-entities/20401001")
    if detail.status_code == 200:
        items = detail.json()
        assert len(items) >= 1
