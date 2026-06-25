import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.database import SessionLocal
from app.capability_discovery.v2.constants import MAX_RESPONSE_LINES
from app.main import app


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def discovery_client() -> TestClient:
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
    "question",
    [
        "¿Qué puedes hacer?",
        "¿Cómo puedes ayudarme?",
        "¿Qué puedo preguntarte?",
    ],
)
def test_integration_capability_discovery_v2(
    discovery_client: TestClient,
    question: str,
) -> None:
    response = discovery_client.post("/api/chat/hybrid", json={"message": question})
    assert response.status_code == 200
    data = response.json()

    assert data["handled_by"] == "capability_discovery"
    assert data["success"] is True
    assert data["answer"].startswith("Puedo ayudarte con información sobre:")
    assert len(data["answer"].splitlines()) <= MAX_RESPONSE_LINES
    assert data["metadata"]["capabilities_count"] == 5
    assert data["metadata"]["example_questions_count"] == 3
    assert data["metadata"]["discovery_version"] == "v2"
    assert data["metadata"]["suggested_questions_count"] == 0
    assert data["metadata"]["suggested_questions_generated"] is False
    assert data.get("suggestions") is None or data["suggestions"]["questions"] == []
