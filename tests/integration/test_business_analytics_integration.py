import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.database import SessionLocal
from app.main import app


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def analytics_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        session.execute(
            text(
                """
                ALTER TABLE performance_metrics
                ADD COLUMN IF NOT EXISTS suggested_questions_count INTEGER
                """
            )
        )
        session.execute(
            text(
                """
                ALTER TABLE performance_metrics
                ADD COLUMN IF NOT EXISTS route_type VARCHAR(50)
                """
            )
        )
        session.execute(
            text(
                """
                ALTER TABLE performance_metrics
                ADD COLUMN IF NOT EXISTS response_success BOOLEAN
                """
            )
        )
        session.execute(
            text(
                """
                ALTER TABLE performance_metrics
                ADD COLUMN IF NOT EXISTS deterministic_resolution BOOLEAN
                """
            )
        )
        session.execute(
            text(
                """
                ALTER TABLE performance_metrics
                ADD COLUMN IF NOT EXISTS used_ai BOOLEAN
                """
            )
        )
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    return TestClient(app)


def test_integration_analytics_coverage(analytics_client: TestClient) -> None:
    response = analytics_client.get("/api/analytics/coverage")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "business_pipeline_pct" in data
    assert "legacy_chat_pct" in data


def test_integration_analytics_performance(analytics_client: TestClient) -> None:
    response = analytics_client.get("/api/analytics/performance")
    assert response.status_code == 200
    data = response.json()
    assert "p50_ms" in data
    assert "avg_total_ms" in data


def test_integration_analytics_financial(analytics_client: TestClient) -> None:
    response = analytics_client.get("/api/analytics/financial")
    assert response.status_code == 200
    data = response.json()
    assert "ai_avoidance_rate" in data
    assert "legacy_dependency_rate" in data
    assert data["estimated_gpt_cost"] >= 0


def test_integration_analytics_top_queries(analytics_client: TestClient) -> None:
    response = analytics_client.get("/api/analytics/top-queries?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_integration_analytics_report(analytics_client: TestClient) -> None:
    response = analytics_client.get("/api/analytics/report")
    assert response.status_code == 200
    data = response.json()
    assert "coverage_score" in data
    assert 0 <= data["coverage_score"] <= 100
    assert "top_routes" in data
