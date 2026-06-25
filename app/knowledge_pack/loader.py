"""Fachada legacy: delega en Enterprise Knowledge Service."""

from app.enterprise_knowledge_service.service import get_enterprise_knowledge_platform_service
from app.knowledge_pack.schemas import KnowledgePackItem


def clear_knowledge_pack_cache() -> None:
    get_enterprise_knowledge_platform_service().invalidate_cache()


def _to_item(doc) -> KnowledgePackItem:
    return KnowledgePackItem(
        id=doc.id,
        title=doc.title,
        category=doc.category,
        path=doc.path,
        content=doc.content,
        sections=doc.sections,
    )


def list_by_category(category: str) -> list[KnowledgePackItem]:
    service = get_enterprise_knowledge_platform_service()
    return [_to_item(doc) for doc in service._repository.by_category(category)]


def search_items(query: str, *, limit: int = 50) -> list[KnowledgePackItem]:
    service = get_enterprise_knowledge_platform_service()
    result = service.search(query, limit=limit)
    return [_to_item(doc) for doc in result.items]
