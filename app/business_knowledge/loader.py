"""Fachada de compatibilidad: delega en Enterprise Knowledge Service."""

from app.enterprise_knowledge_service.cache.store import (
    get_knowledge_cache_store,
    reset_knowledge_cache_store,
)
from app.enterprise_knowledge_service.constants import CATEGORY_LABELS
from app.enterprise_knowledge_service.providers.knowledge_pack import CAPABILITIES_DOC_ID, PACK_ROOT
from app.enterprise_knowledge_service.schemas import KnowledgeDocument
from app.enterprise_knowledge_service.service import get_enterprise_knowledge_platform_service


class _KnowledgeCache:
    def __init__(self) -> None:
        snapshot = get_knowledge_cache_store().ensure_loaded()
        self.signature = snapshot.signature
        self.documents = snapshot.documents
        self.faq_answers = snapshot.faq_answers
        self.capabilities = snapshot.capabilities
        self.examples = snapshot.examples
        self.intro_line = snapshot.intro_line
        self.examples_line = snapshot.examples_line


def reload_knowledge_cache() -> _KnowledgeCache:
    get_knowledge_cache_store().ensure_loaded()
    return get_knowledge_cache()


def get_knowledge_cache() -> _KnowledgeCache:
    return _KnowledgeCache()


def invalidate_knowledge_cache() -> None:
    from app.enterprise_knowledge_service.cache.store import reset_knowledge_cache_store
    from app.enterprise_knowledge_service.metrics import reset_enterprise_knowledge_metrics
    from app.enterprise_knowledge_service.service import reset_enterprise_knowledge_platform_service

    reset_enterprise_knowledge_metrics()
    reset_knowledge_cache_store()
    reset_enterprise_knowledge_platform_service()
    get_knowledge_cache_store().ensure_loaded()


def list_documents_by_category(category: str) -> list[KnowledgeDocument]:
    return get_enterprise_knowledge_platform_service()._repository.by_category(category)


def get_all_documents() -> list[KnowledgeDocument]:
    return list(get_enterprise_knowledge_platform_service()._repository.all_documents())


def search_documents(query: str, *, limit: int = 50) -> list[KnowledgeDocument]:
    return get_enterprise_knowledge_platform_service().search(query, limit=limit).items


def get_faq_answer(question: str) -> str | None:
    return get_enterprise_knowledge_platform_service().get_faq(question)


def get_capabilities_payload() -> tuple[str, list[str], list[str]]:
    payload = get_enterprise_knowledge_platform_service().get_capabilities()
    return payload.answer, payload.capabilities, payload.examples


__all__ = [
    "CATEGORY_LABELS",
    "CAPABILITIES_DOC_ID",
    "PACK_ROOT",
    "get_all_documents",
    "get_capabilities_payload",
    "get_faq_answer",
    "get_knowledge_cache",
    "invalidate_knowledge_cache",
    "list_documents_by_category",
    "reload_knowledge_cache",
    "search_documents",
]
