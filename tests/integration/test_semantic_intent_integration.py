import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.semantic_intent.metrics import SemanticIntentMetrics


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def semantic_client() -> TestClient:
    SemanticIntentMetrics.reset_for_tests()
    return TestClient(app)


def test_integration_verbs(semantic_client: TestClient) -> None:
    response = semantic_client.get("/api/semantic-intent/verbs")
    assert response.status_code == 200
    assert response.json()["enabled_count"] >= 20


def test_integration_parse(semantic_client: TestClient) -> None:
    response = semantic_client.post(
        "/api/semantic-intent/parse",
        json={"question": "Evaluar riesgos del cliente principal"},
    )
    assert response.status_code == 200
    assert response.json()["business_verb"]["verb_id"] == "evaluar"


def test_integration_plan(semantic_client: TestClient) -> None:
    response = semantic_client.post(
        "/api/semantic-intent/plan",
        json={"question": "Recomendar acciones para proveedores"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["execution_strategy"] == "ero_recommendation_review"
    assert len(body["required_reasoning"]) > 0


def test_integration_statistics(semantic_client: TestClient) -> None:
    response = semantic_client.get("/api/semantic-intent/statistics")
    assert response.status_code == 200
    assert "semantic_parses" in response.json()


def test_integration_metrics_summary(semantic_client: TestClient) -> None:
    response = semantic_client.get("/api/metrics/summary")
    assert response.status_code == 200
    assert "semantic_parses" in response.json()
