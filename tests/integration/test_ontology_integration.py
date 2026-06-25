import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.business_ontology.metrics import BusinessOntologyMetrics
from app.database.database import SessionLocal, engine
from app.main import app
from app.models.business_ontology import (
    BusinessOntologyAssignment,
    BusinessOntologyRule,
    BusinessOntologyType,
)
from app.models.canonical_business_entity import CanonicalBusinessEntity


pytestmark = pytest.mark.integration


def _ensure_tables() -> None:
    inspector = inspect(engine)
    names = set(inspector.get_table_names())
    for model in (
        CanonicalBusinessEntity,
        BusinessOntologyType,
        BusinessOntologyRule,
        BusinessOntologyAssignment,
    ):
        if model.__tablename__ not in names:
            model.__table__.create(bind=engine)


@pytest.fixture(scope="module")
def ontology_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        _ensure_tables()
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    BusinessOntologyMetrics.reset_for_tests()
    return TestClient(app)


def test_integration_ontology_list(ontology_client: TestClient) -> None:
    response = ontology_client.get("/api/business-ontology?page=1&page_size=5")
    assert response.status_code == 200
    assert "items" in response.json()


def test_integration_ontology_types(ontology_client: TestClient) -> None:
    response = ontology_client.get("/api/business-ontology/types")
    assert response.status_code == 200


def test_integration_ontology_statistics(ontology_client: TestClient) -> None:
    response = ontology_client.get("/api/business-ontology/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "ontology_entities" in data


def test_integration_metrics_ontology_fields(ontology_client: TestClient) -> None:
    response = ontology_client.get("/api/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "ontology_pending" in data
    assert "ontology_rules" in data
