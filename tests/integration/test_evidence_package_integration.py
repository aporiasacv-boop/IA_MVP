import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.database.database import SessionLocal, engine
from app.evidence_package.metrics import EvidencePackageMetrics
from app.main import app
from app.models.canonical_business_entity import CanonicalBusinessEntity
from app.models.enterprise_knowledge_object import EnterpriseKnowledgeObject
from app.models.enterprise_reasoning_object import EnterpriseReasoningObject


pytestmark = pytest.mark.integration


def _ensure_tables() -> None:
    inspector = inspect(engine)
    names = set(inspector.get_table_names())
    for model in (
        CanonicalBusinessEntity,
        EnterpriseKnowledgeObject,
        EnterpriseReasoningObject,
    ):
        if model.__tablename__ not in names:
            model.__table__.create(bind=engine)


@pytest.fixture(scope="module")
def evidence_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        _ensure_tables()
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    EvidencePackageMetrics.reset_for_tests()
    return TestClient(app)


def test_integration_evidence_schema(evidence_client: TestClient) -> None:
    response = evidence_client.get("/api/evidence/schema")
    assert response.status_code == 200
    assert response.json()["schema_id"] == "enterprise_evidence_package_v1"


def test_integration_evidence_build(evidence_client: TestClient) -> None:
    response = evidence_client.post(
        "/api/evidence/build",
        json={"question": "Evaluar riesgos del cliente principal"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["contains_sql"] is False
    assert "execution_plan" in body


def test_integration_evidence_example(evidence_client: TestClient) -> None:
    response = evidence_client.get("/api/evidence/example")
    assert response.status_code == 200
    assert response.json()["metadata"]["contains_llm_output"] is False


def test_integration_evidence_statistics(evidence_client: TestClient) -> None:
    response = evidence_client.get("/api/evidence/statistics")
    assert response.status_code == 200
    assert "evidence_packages_total" in response.json()


def test_integration_metrics_evidence(evidence_client: TestClient) -> None:
    response = evidence_client.get("/api/metrics/summary")
    assert response.status_code == 200
    assert "evidence_packages_total" in response.json()
