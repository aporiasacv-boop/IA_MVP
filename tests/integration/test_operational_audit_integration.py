import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.database import SessionLocal
from app.main import app


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def audit_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1 FROM performance_metrics LIMIT 1"))
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    return TestClient(app)


def test_integration_audit_overview(audit_client: TestClient) -> None:
    response = audit_client.get("/api/audit/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "coverage_gap_score" in data
    assert 0 <= data["coverage_score"] <= 100
    assert 0 <= data["coverage_gap_score"] <= 100


def test_integration_audit_coverage_gaps(audit_client: TestClient) -> None:
    response = audit_client.get("/api/audit/coverage-gaps")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_integration_audit_top_routes(audit_client: TestClient) -> None:
    response = audit_client.get("/api/audit/top-routes")
    assert response.status_code == 200
    data = response.json()
    if data:
        assert "route" in data[0]
        assert "percentage" in data[0]


def test_integration_audit_top_failures(audit_client: TestClient) -> None:
    response = audit_client.get("/api/audit/top-failures")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_integration_audit_adoption(audit_client: TestClient) -> None:
    response = audit_client.get("/api/audit/adoption")
    assert response.status_code == 200
    data = response.json()
    assert "suggested_questions_usage" in data


def test_integration_audit_export_json(audit_client: TestClient) -> None:
    response = audit_client.get("/api/audit/coverage-gaps/export?format=json")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


def test_integration_audit_export_csv(audit_client: TestClient) -> None:
    response = audit_client.get("/api/audit/coverage-gaps/export?format=csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "question" in response.text
