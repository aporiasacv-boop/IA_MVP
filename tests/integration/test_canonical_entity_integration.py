import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.canonical_business_entity.metrics import CanonicalEntityMetrics
from app.database.database import SessionLocal, engine
from app.main import app
from app.models.business_entity_master import BusinessEntityMaster
from app.models.canonical_business_entity import (
    BusinessEntityResolution,
    CanonicalBusinessEntity,
    CanonicalEntitySuggestion,
)


pytestmark = pytest.mark.integration


def _ensure_tables() -> None:
    inspector = inspect(engine)
    names = set(inspector.get_table_names())
    for model in (BusinessEntityMaster, CanonicalBusinessEntity, BusinessEntityResolution, CanonicalEntitySuggestion):
        if model.__tablename__ not in names:
            model.__table__.create(bind=engine)


@pytest.fixture(scope="module")
def canonical_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        _ensure_tables()
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    CanonicalEntityMetrics.reset_for_tests()
    return TestClient(app)


def test_integration_canonical_list(canonical_client: TestClient) -> None:
    response = canonical_client.get("/api/canonical-entities?page=1&page_size=5")
    assert response.status_code == 200
    assert "items" in response.json()


def test_integration_canonical_statistics(canonical_client: TestClient) -> None:
    response = canonical_client.get("/api/canonical-entities/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "canonical_entities_total" in data
    assert "unresolved_pct" in data


def test_integration_metrics_summary_canonical_fields(canonical_client: TestClient) -> None:
    response = canonical_client.get("/api/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "canonical_entities_total" in data
    assert "pending_matches" in data
