from app.enterprise_knowledge_service.cache.store import get_knowledge_cache_store
from app.enterprise_knowledge_service.schemas import KnowledgeDocument


class KnowledgeRepository:
    """Acceso unificado a documentos en cache central."""

    def __init__(self) -> None:
        self._cache = get_knowledge_cache_store()

    def all_documents(self) -> tuple[KnowledgeDocument, ...]:
        return self._cache.ensure_loaded().documents

    def by_category(self, category: str) -> list[KnowledgeDocument]:
        return [d for d in self.all_documents() if d.category == category]

    def by_id(self, doc_id: str) -> KnowledgeDocument | None:
        for doc in self.all_documents():
            if doc.id == doc_id:
                return doc
        return None

    def exists(self, doc_id: str) -> bool:
        return self.by_id(doc_id) is not None

    def faq_answers(self) -> dict[str, str]:
        return dict(self._cache.ensure_loaded().faq_answers)

    def capabilities(self) -> tuple[str, ...]:
        return self._cache.ensure_loaded().capabilities

    def examples(self) -> tuple[str, ...]:
        return self._cache.ensure_loaded().examples

    def intro_line(self) -> str:
        return self._cache.ensure_loaded().intro_line

    def examples_line(self) -> str:
        return self._cache.ensure_loaded().examples_line

    def provider_distribution(self) -> dict[str, int]:
        return dict(self._cache.ensure_loaded().provider_distribution)

    def invalidate(self) -> None:
        self._cache.invalidate()
