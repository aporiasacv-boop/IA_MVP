import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.database import SessionLocal
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
        "¿Cómo puedes ayudarme?",
    ],
)
def test_integration_capability_discovery_v2(
    discovery_client: TestClient,
    question: str,
) -> None:
    response = discovery_client.post("/api/chat/hybrid", json={"message": question})
    assert response.status_code == 200
    data = response.json()

    assert data["handled_by"] == "business_knowledge"
    assert data["success"] is True
    assert "Clientes" in data["answer"] or "clientes" in data["answer"].lower()


def test_integration_business_knowledge_capability_question(
    discovery_client: TestClient,
) -> None:
    response = discovery_client.post("/api/chat/hybrid", json={"message": "¿Qué puedo preguntarte?"})
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "business_knowledge"
    assert data["metadata"]["knowledge_match_type"] == "capabilities"


def test_integration_product_identity_capabilities(
    discovery_client: TestClient,
) -> None:
    response = discovery_client.post("/api/chat/hybrid", json={"message": "¿Qué puedes hacer?"})
    assert response.status_code == 200
    data = response.json()

    assert data["handled_by"] == "product_identity"
    assert data["success"] is True
    assert "Olnatura Intelligence" in data["answer"]
