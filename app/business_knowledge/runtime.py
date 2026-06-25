from datetime import datetime, timezone

from app.business_knowledge.schemas import (
    KnowledgeCategoriesResponse,
    KnowledgeCategorySummary,
    KnowledgeDocument,
    KnowledgeRuntimeHealthResponse,
    KnowledgeRuntimeStatistics,
    KnowledgeSearchResult,
)
from app.enterprise_knowledge_service.constants import CATEGORY_LABELS
from app.enterprise_knowledge_service.health import build_health_response
from app.enterprise_knowledge_service.metrics import get_enterprise_knowledge_metrics
from app.enterprise_knowledge_service.providers.knowledge_pack import PACK_ROOT
from app.enterprise_knowledge_service.repository.repository import KnowledgeRepository
from app.enterprise_knowledge_service.search.engine import KnowledgeSearchEngine


class BusinessKnowledgeRuntime:
    """Fachada legacy sobre Enterprise Knowledge Service."""

    def __init__(self) -> None:
        self._repository = KnowledgeRepository()
        self._search = KnowledgeSearchEngine(self._repository)

    def search(self, query: str, *, limit: int = 50) -> KnowledgeSearchResult:
        result = self._search.search(query, limit=limit)
        items = [
            KnowledgeDocument.model_validate(doc.model_dump(exclude={"provider"}))
            for doc in result.items
        ]
        return KnowledgeSearchResult(query=result.query, total=result.total, items=items)

    def list_categories(self) -> KnowledgeCategoriesResponse:
        counts: dict[str, int] = {}
        for doc in self._repository.all_documents():
            counts[doc.category] = counts.get(doc.category, 0) + 1
        categories = [
            KnowledgeCategorySummary(
                category=category,
                label=CATEGORY_LABELS.get(category, category.title()),
                count=count,
            )
            for category, count in sorted(counts.items())
        ]
        return KnowledgeCategoriesResponse(
            categories=categories,
            total_documents=len(self._repository.all_documents()),
        )

    def get_statistics(self) -> KnowledgeRuntimeStatistics:
        counts: dict[str, int] = {}
        for doc in self._repository.all_documents():
            counts[doc.category] = counts.get(doc.category, 0) + 1
        metrics = get_enterprise_knowledge_metrics()
        last_refresh = metrics.last_refresh
        if isinstance(last_refresh, datetime) and last_refresh.tzinfo is None:
            last_refresh = last_refresh.replace(tzinfo=timezone.utc)
        return KnowledgeRuntimeStatistics(
            total_documents=len(self._repository.all_documents()),
            documents_by_category=counts,
            faq_entries=len(self._repository.faq_answers()),
            knowledge_runtime_hits=metrics.hits,
            knowledge_runtime_misses=metrics.misses,
            knowledge_runtime_cache_hits=metrics.cache_hits,
            knowledge_runtime_reload_time_ms=metrics.reload_time_ms,
            knowledge_runtime_last_refresh=last_refresh,
        )

    def get_health(self) -> KnowledgeRuntimeHealthResponse:
        health = build_health_response()
        return KnowledgeRuntimeHealthResponse(
            status=health.status,
            pack_root_exists=PACK_ROOT.exists(),
            total_documents=health.total_documents,
            last_refresh=health.last_refresh,
            cache_valid=health.cache_valid,
        )

    def list_by_category(self, category: str):
        return self._repository.by_category(category)

    def all_documents(self):
        return list(self._repository.all_documents())
