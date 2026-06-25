import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.database.database import SessionLocal, engine
from app.enterprise_knowledge.metrics import EnterpriseKnowledgeMetrics
from app.main import app
from app.models.canonical_business_entity import CanonicalBusinessEntity
from app.models.enterprise_knowledge_object import EnterpriseKnowledgeObject


pytestmark = pytest.mark.integration


def _ensure_tables() -> None:
    inspector = inspect(engine)
    names = set(inspector.get_table_names())
    for model in (CanonicalBusinessEntity, EnterpriseKnowledgeObject):
        if model.__tablename__ not in names:
            model.__table__.create(bind=engine)


@pytest.fixture(scope="module")
def knowledge_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        _ensure_tables()
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    EnterpriseKnowledgeMetrics.reset_for_tests()
    return TestClient(app)


def test_integration_knowledge_list(knowledge_client: TestClient) -> None:
    response = knowledge_client.get("/api/knowledge/entities?page=1&page_size=5")
    assert response.status_code == 200


def test_integration_knowledge_schema(knowledge_client: TestClient) -> None:
    response = knowledge_client.get("/api/knowledge/schema")
    assert response.status_code == 200
    assert response.json()["schema_id"] == "enterprise_knowledge_object_v1"


def test_integration_knowledge_statistics(knowledge_client: TestClient) -> None:
    response = knowledge_client.get("/api/knowledge/statistics")
    assert response.status_code == 200
    assert "knowledge_objects_total" in response.json()


def test_integration_metrics_knowledge_fields(knowledge_client: TestClient) -> None:
    response = knowledge_client.get("/api/metrics/summary")
    assert response.status_code == 200
    assert "knowledge_objects_total" in response.json()
