import pytest
from fastapi.testclient import TestClient

from app.knowledge_pack.loader import clear_knowledge_pack_cache
from app.main import app


@pytest.fixture
def client() -> TestClient:
    clear_knowledge_pack_cache()
    return TestClient(app)


def test_api_concepts(client: TestClient) -> None:
    response = client.get("/api/knowledge-pack/concepts")
    assert response.status_code == 200
    assert response.json()["total"] == 30


def test_api_rules(client: TestClient) -> None:
    response = client.get("/api/knowledge-pack/rules")
    assert response.status_code == 200
    assert response.json()["total"] >= 40


def test_api_search(client: TestClient) -> None:
    response = client.get("/api/knowledge-pack/search", params={"q": "proveedor"})
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_api_faq_and_glossary(client: TestClient) -> None:
    faq = client.get("/api/knowledge-pack/faq")
    glossary = client.get("/api/knowledge-pack/glossary")
    assert faq.status_code == 200
    assert glossary.status_code == 200
