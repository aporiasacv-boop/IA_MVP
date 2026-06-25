"""Pruebas del Business Knowledge Runtime."""

import pytest
from fastapi.testclient import TestClient

from app.business_knowledge.loader import (
    get_all_documents,
    get_capabilities_payload,
    get_faq_answer,
    get_knowledge_cache,
    invalidate_knowledge_cache,
    reload_knowledge_cache,
)
from app.business_knowledge.matcher import (
    is_identity_institutional_question,
    resolve_institutional_question,
)
from app.business_knowledge.metrics import get_business_knowledge_metrics, reset_business_knowledge_metrics
from app.business_knowledge.responder import (
    try_business_knowledge_response,
    try_product_identity_from_runtime,
)
from app.business_knowledge.runtime import BusinessKnowledgeRuntime
from app.main import app


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    reset_business_knowledge_metrics()
    invalidate_knowledge_cache()


def test_runtime_loads_knowledge_pack_documents() -> None:
    reload_knowledge_cache()
    documents = get_all_documents()
    assert len(documents) >= 100
    categories = {doc.category for doc in documents}
    assert "concepts" in categories
    assert "faq" in categories
    assert "rules" in categories
    assert "glossary" in categories
    assert "executive" in categories
    assert "examples" in categories
    assert "scenarios" in categories


def test_faq_answer_from_runtime() -> None:
    answer = get_faq_answer("¿Cómo te llamas?")
    assert answer is not None
    assert "Olnatura Intelligence" in answer


def test_identity_questions_resolved_from_faq() -> None:
    for question in (
        "¿Cómo te llamas?",
        "¿Quién eres?",
        "¿Qué haces?",
        "¿Qué puedes hacer?",
        "¿Quién te creó?",
        "¿Cómo obtienes la información?",
    ):
        assert is_identity_institutional_question(question)
        resolved = resolve_institutional_question(question)
        assert resolved is not None
        assert resolved.source.startswith("knowledge_pack")


def test_definition_question_from_faq() -> None:
    resolved = resolve_institutional_question("¿Qué es un proveedor?")
    assert resolved is not None
    assert "contraparte" in resolved.answer.lower()


def test_capability_discovery_from_knowledge_pack() -> None:
    resolved = resolve_institutional_question("¿Qué puedo preguntarte?")
    assert resolved is not None
    assert resolved.match_type == "capabilities"
    answer, caps, examples = get_capabilities_payload()
    assert len(caps) >= 3
    assert len(examples) >= 2
    assert "Clientes" in answer


def test_product_identity_responder_uses_runtime() -> None:
    result = try_product_identity_from_runtime("¿Cómo te llamas?")
    assert result is not None
    assert result.handled_by == "product_identity"
    assert "Olnatura Intelligence" in result.answer


def test_business_knowledge_responder_skips_identity() -> None:
    assert try_business_knowledge_response("¿Quién eres?") is None


def test_business_knowledge_responder_faq_and_capabilities() -> None:
    faq = try_business_knowledge_response("¿Qué es una cuenta contable?")
    assert faq is not None
    assert faq.handled_by == "business_knowledge"

    caps = try_business_knowledge_response("¿Qué sabes hacer?")
    assert caps is not None
    assert caps.handled_by == "business_knowledge"


def test_cache_hit_increments_metrics() -> None:
    reload_knowledge_cache()
    metrics = get_business_knowledge_metrics()
    before = metrics.cache_hits
    get_knowledge_cache()
    assert get_business_knowledge_metrics().cache_hits >= before


def test_miss_increments_on_unknown_question() -> None:
    resolve_institutional_question("¿Cuántos widgets hay en Marte?")
    assert get_business_knowledge_metrics().misses >= 1


def test_runtime_service_statistics() -> None:
    runtime = BusinessKnowledgeRuntime()
    stats = runtime.get_statistics()
    assert stats.total_documents >= 100
    assert stats.faq_entries >= 10


def test_runtime_search() -> None:
    runtime = BusinessKnowledgeRuntime()
    result = runtime.search("cliente")
    assert result.total > 0


def test_api_health_statistics_search_categories() -> None:
    client = TestClient(app)
    health = client.get("/api/business-knowledge/health")
    assert health.status_code == 200
    assert health.json()["status"] in {"ok", "degraded"}

    stats = client.get("/api/business-knowledge/statistics")
    assert stats.status_code == 200
    assert stats.json()["total_documents"] >= 100

    search = client.get("/api/business-knowledge/search", params={"q": "proveedor"})
    assert search.status_code == 200
    assert search.json()["total"] > 0

    categories = client.get("/api/business-knowledge/categories")
    assert categories.status_code == 200
    assert categories.json()["total_documents"] >= 100


def test_hybrid_chat_institutional_via_runtime() -> None:
    client = TestClient(app)
    response = client.post("/api/chat/hybrid", json={"message": "¿Qué es un cliente?"})
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "business_knowledge"
    assert "contraparte" in data["answer"].lower()
