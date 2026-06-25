import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.business_entity_profile.metrics import EntityProfileMetrics
from app.database.database import SessionLocal, engine
from app.main import app
from app.models.business_entity_profile import BusinessEntityProfile
from app.models.business_entity_master import BusinessEntityMaster
from app.models.canonical_business_entity import (
    BusinessEntityResolution,
    CanonicalBusinessEntity,
)


pytestmark = pytest.mark.integration


def _ensure_tables() -> None:
    inspector = inspect(engine)
    names = set(inspector.get_table_names())
    for model in (
        BusinessEntityMaster,
        CanonicalBusinessEntity,
        BusinessEntityResolution,
        BusinessEntityProfile,
    ):
        if model.__tablename__ not in names:
            model.__table__.create(bind=engine)


@pytest.fixture(scope="module")
def profile_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        _ensure_tables()
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    EntityProfileMetrics.reset_for_tests()
    return TestClient(app)


def test_integration_entity_profiles_list(profile_client: TestClient) -> None:
    response = profile_client.get("/api/entity-profiles?page=1&page_size=5")
    assert response.status_code == 200
    assert "items" in response.json()


def test_integration_entity_profiles_statistics(profile_client: TestClient) -> None:
    response = profile_client.get("/api/entity-profiles/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "entity_profiles_total" in data
    assert "average_profile_completeness" in data


def test_integration_metrics_summary_profile_fields(profile_client: TestClient) -> None:
    response = profile_client.get("/api/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "entity_profiles_total" in data
    assert "last_profile_refresh" in data
