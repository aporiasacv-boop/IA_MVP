import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.ai_orchestration.metrics import LLMOrchestrationMetrics
from app.database.database import SessionLocal, engine
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
def orchestration_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        _ensure_tables()
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    LLMOrchestrationMetrics.reset_for_tests()
    return TestClient(app)


def test_integration_executive_schema(orchestration_client: TestClient) -> None:
    response = orchestration_client.get("/api/executive-response/schema")
    assert response.status_code == 200
    assert response.json()["schema_id"] == "executive_response_v1"


def test_integration_executive_generate(orchestration_client: TestClient) -> None:
    response = orchestration_client.post(
        "/api/executive-response/generate",
        json={"question": "Evaluar riesgos del cliente principal"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    assert "executive_summary" in body


def test_integration_ai_costs(orchestration_client: TestClient) -> None:
    orchestration_client.post(
        "/api/executive-response/generate",
        json={"question": "Recomendar acciones para proveedores"},
    )
    response = orchestration_client.get("/api/ai-costs/summary")
    assert response.status_code == 200
    assert response.json()["llm_requests"] >= 1


def test_integration_metrics_llm_fields(orchestration_client: TestClient) -> None:
    response = orchestration_client.get("/api/metrics/summary")
    assert response.status_code == 200
    assert "llm_requests" in response.json()
