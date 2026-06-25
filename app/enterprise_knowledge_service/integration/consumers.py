"""Hooks de integración para consumidores enterprise sin acoplar al Runtime."""

from app.enterprise_knowledge_service.schemas import BusinessContextRequest, CapabilitiesPayload
from app.enterprise_knowledge_service.service import get_enterprise_knowledge_platform_service


def knowledge_for_chat(message: str):
    from app.enterprise_knowledge_service.runtime.responder import (
        try_business_knowledge_response,
        try_product_identity_from_runtime,
    )

    return try_product_identity_from_runtime(message), try_business_knowledge_response(message)


def knowledge_for_product_identity(question: str) -> str | None:
    from app.enterprise_knowledge_service.runtime.matcher import get_institutional_matcher

    matcher = get_institutional_matcher()
    if not matcher.is_identity_institutional_question(question):
        return None
    resolved = matcher.resolve_institutional_question(question)
    return resolved.answer if resolved else None


def knowledge_for_capability_discovery() -> CapabilitiesPayload:
    return get_enterprise_knowledge_platform_service().get_capabilities()


def knowledge_for_guided_fallback(question: str) -> str | None:
    result = get_enterprise_knowledge_platform_service().search(question, limit=1)
    if not result.items:
        return None
    return result.items[0].content[:500]


def knowledge_for_eko() -> dict:
    service = get_enterprise_knowledge_platform_service()
    return {
        "concepts": len(service._repository.by_category("concepts")),
        "rules": len(service._repository.by_category("rules")),
    }


def knowledge_for_ero() -> dict:
    return {"executive_documents": get_enterprise_knowledge_platform_service().get_executive_context()}


def knowledge_for_sbep() -> CapabilitiesPayload:
    return get_enterprise_knowledge_platform_service().get_capabilities()


def knowledge_for_eep(question: str, *, canonical_id: int | None = None):
    return get_enterprise_knowledge_platform_service().get_business_context(
        BusinessContextRequest(question=question, canonical_id=canonical_id)
    )


def knowledge_for_executive_reasoning(question: str) -> str | None:
    payload = get_enterprise_knowledge_platform_service().get_capabilities()
    if question.strip():
        search = get_enterprise_knowledge_platform_service().search(question, limit=1)
        if search.items:
            return search.items[0].content[:800]
    return payload.answer
