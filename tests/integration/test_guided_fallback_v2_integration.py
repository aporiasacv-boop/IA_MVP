import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.database import SessionLocal
from app.main import app


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def fallback_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL no disponible: {exc}")
    session.close()
    return TestClient(app)


@pytest.mark.parametrize(
    ("question", "expected_domain", "domain_label"),
    [
        ("¿Cómo van las ventas?", "VENTAS", "ventas"),
        ("¿Cómo está el inventario?", "INVENTARIO", "inventario"),
        ("¿Cómo van las compras?", "COMPRAS", "compras"),
        ("¿Qué información financiera tienes?", "FINANZAS", "finanzas"),
    ],
)
def test_integration_domain_contextual_fallback(
    fallback_client: TestClient,
    question: str,
    expected_domain: str,
    domain_label: str,
) -> None:
    response = fallback_client.post("/api/chat/hybrid", json={"message": question})
    assert response.status_code == 200
    data = response.json()

    assert data["handled_by"] == "guided_fallback"
    assert f"Detecté una consulta relacionada con {domain_label}." in data["answer"]
    assert data["metadata"]["domain_detected"] == expected_domain
    assert data["metadata"]["domain_contextual"] is True
    assert data["answer"].count("•") == 4


def test_integration_metrics_summary_includes_domain_metrics(
    fallback_client: TestClient,
) -> None:
    fallback_client.post("/api/chat/hybrid", json={"message": "¿Cómo van las ventas?"})

    summary = fallback_client.get("/api/metrics/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert "domain_fallback_hits" in payload
    assert "domain_fallback_misses" in payload
    assert "top_domains" in payload


def test_integration_audit_report_includes_domain_metrics(
    fallback_client: TestClient,
) -> None:
    fallback_client.post("/api/chat/hybrid", json={"message": "¿Cómo van las compras?"})

    report = fallback_client.get("/api/audit/report")
    assert report.status_code == 200
    payload = report.json()
    assert "overview" in payload
    assert "domain_fallback" in payload
    assert payload["domain_fallback"]["domain_detected"] == "COMPRAS"
    assert payload["domain_fallback"]["domain_fallback_hits"] >= 1
