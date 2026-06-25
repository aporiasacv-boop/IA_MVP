"""Pruebas del Enterprise Knowledge Service (EKS)."""

import pytest
from fastapi.testclient import TestClient

from app.enterprise_knowledge_service.metrics import (
    get_enterprise_knowledge_metrics,
    reset_enterprise_knowledge_metrics,
)
from app.enterprise_knowledge_service.runtime.matcher import get_institutional_matcher
from app.enterprise_knowledge_service.runtime.responder import (
    try_business_knowledge_response,
    try_product_identity_from_runtime,
)
from app.enterprise_knowledge_service.service import (
    EnterpriseKnowledgePlatformService,
    get_enterprise_knowledge_platform_service,
    reset_enterprise_knowledge_platform_service,
)
from app.business_knowledge.loader import invalidate_knowledge_cache
from app.main import app


@pytest.fixture(autouse=True)
def reset_eks_state() -> None:
    reset_enterprise_knowledge_metrics()
    reset_enterprise_knowledge_platform_service()
    invalidate_knowledge_cache()


def test_eks_loads_documents() -> None:
    service = get_enterprise_knowledge_platform_service()
    categories = service.list_categories()
    assert categories.total_documents >= 100


def test_eks_search_get_faq_get_capabilities() -> None:
    service = EnterpriseKnowledgePlatformService()
    search = service.search("proveedor")
    assert search.total > 0
    faq = service.get_faq("¿Cómo te llamas?")
    assert faq is not None
    caps = service.get_capabilities()
    assert len(caps.capabilities) >= 3


def test_eks_exists_and_categories() -> None:
    service = EnterpriseKnowledgePlatformService()
    assert service.exists("capacidades-asistente")
    categories = service.list_categories()
    assert any(item.category == "faq" for item in categories.categories)


def test_eks_business_context_stub() -> None:
    from app.enterprise_knowledge_service.schemas import BusinessContextRequest

    service = EnterpriseKnowledgePlatformService()
    context = service.get_business_context(BusinessContextRequest(question="¿Qué es un cliente?"))
    assert context.available is True
    assert context.summary


def test_eks_providers_lists_planned() -> None:
    providers = get_enterprise_knowledge_platform_service().get_providers()
    assert len(providers.active) >= 1
    planned_ids = {item.id for item in providers.planned}
    assert "sharepoint" in planned_ids
    assert "dynamics" in planned_ids
    assert "confluence" in planned_ids


def test_eks_matcher_and_responder() -> None:
    matcher = get_institutional_matcher()
    assert matcher.is_identity_institutional_question("¿Quién eres?")
    resolved = matcher.resolve_institutional_question("¿Qué es un proveedor?")
    assert resolved is not None
    identity = try_product_identity_from_runtime("¿Cómo te llamas?")
    assert identity is not None
    assert identity.handled_by == "product_identity"
    business = try_business_knowledge_response("¿Qué es una cuenta contable?")
    assert business is not None
    assert business.handled_by == "business_knowledge"


def test_eks_metrics_increment() -> None:
    service = EnterpriseKnowledgePlatformService()
    before = get_enterprise_knowledge_metrics().knowledge_requests
    service.search("cliente")
    assert get_enterprise_knowledge_metrics().knowledge_requests >= before + 1


def test_eks_api_endpoints() -> None:
    client = TestClient(app)
    health = client.get("/api/enterprise-knowledge/health")
    assert health.status_code == 200
    assert health.json()["status"] in {"ok", "degraded"}

    stats = client.get("/api/enterprise-knowledge/statistics")
    assert stats.status_code == 200
    assert stats.json()["total_documents"] >= 100
    assert "cache_hit_rate" in stats.json()

    providers = client.get("/api/enterprise-knowledge/providers")
    assert providers.status_code == 200
    assert len(providers.json()["active"]) >= 1

    search = client.get("/api/enterprise-knowledge/search", params={"q": "cliente"})
    assert search.status_code == 200
    assert search.json()["total"] > 0


def test_eks_getters_and_runtime() -> None:
    from app.enterprise_knowledge_service.integration import consumers
    from app.enterprise_knowledge_service.runtime.business_knowledge_runtime import BusinessKnowledgeRuntime
    from app.enterprise_knowledge_service.providers.base import (
        ConfluenceProvider,
        DatabaseProvider,
        DynamicsProvider,
        PDFProvider,
        SharePointProvider,
    )

    service = EnterpriseKnowledgePlatformService()
    assert service.get_concept("capacidades-asistente") is None
    concepts = service._repository.by_category("concepts")
    if concepts:
        assert service.get_concept(concepts[0].id) is not None
    rules = service._repository.by_category("rules")
    if rules:
        assert service.get_rule(rules[0].id) is not None
    assert isinstance(service.get_glossary(), list)
    assert isinstance(service.get_examples(), list)
    assert len(service.get_executive_context()) >= 1
    service.invalidate_cache()

    runtime = BusinessKnowledgeRuntime()
    assert runtime.get_health().status in {"ok", "degraded"}
    assert runtime.list_categories().total_documents >= 100

    for provider in (
        DatabaseProvider(),
        SharePointProvider(),
        PDFProvider(),
        DynamicsProvider(),
        ConfluenceProvider(),
    ):
        assert provider.is_available() is False
        assert provider.load_documents() == []

    assert consumers.knowledge_for_capability_discovery().answer
    assert consumers.knowledge_for_eko()["concepts"] >= 0
    assert consumers.knowledge_for_ero()["executive_documents"]
    assert consumers.knowledge_for_sbep().capabilities
    assert consumers.knowledge_for_eep("cliente").available
    assert consumers.knowledge_for_executive_reasoning("cliente")
    identity, business = consumers.knowledge_for_chat("¿Quién eres?")
    assert identity is not None


def test_eks_definition_and_capability_matchers() -> None:
    matcher = get_institutional_matcher()
    caps = matcher.resolve_institutional_question("¿Qué puedo preguntarte?")
    assert caps is not None
    assert caps.match_type == "capabilities"
    assert matcher.resolve_institutional_question("") is None
    assert matcher.resolve_institutional_question("¿Cuántos widgets en Marte?") is None
