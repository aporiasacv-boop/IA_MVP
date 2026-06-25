from datetime import datetime, timezone

from app.enterprise_knowledge_service.constants import CATEGORY_LABELS
from app.enterprise_knowledge_service.health import build_health_response
from app.enterprise_knowledge_service.metrics import get_enterprise_knowledge_metrics
from app.enterprise_knowledge_service.repository.repository import KnowledgeRepository
from app.enterprise_knowledge_service.schemas import (
    EnterpriseKnowledgeHealthResponse,
    EnterpriseKnowledgeStatistics,
    KnowledgeCategoriesResponse,
    KnowledgeCategorySummary,
    KnowledgeSearchResult,
)
from app.enterprise_knowledge_service.search.engine import KnowledgeSearchEngine


class BusinessKnowledgeRuntime:
    """Componente interno BKR expuesto vía Enterprise Knowledge Service."""

    def __init__(self) -> None:
        self._service_repository = KnowledgeRepository()
        self._search = KnowledgeSearchEngine(self._service_repository)

    def search(self, query: str, *, limit: int = 50) -> KnowledgeSearchResult:
        return self._search.search(query, limit=limit)

    def list_categories(self) -> KnowledgeCategoriesResponse:
        counts: dict[str, int] = {}
        for doc in self._service_repository.all_documents():
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
            total_documents=len(self._service_repository.all_documents()),
        )

    def get_statistics(self) -> EnterpriseKnowledgeStatistics:
        counts: dict[str, int] = {}
        for doc in self._service_repository.all_documents():
            counts[doc.category] = counts.get(doc.category, 0) + 1
        metrics = get_enterprise_knowledge_metrics()
        metrics.set_provider_distribution(self._service_repository.provider_distribution())
        last_refresh = metrics.last_refresh
        if isinstance(last_refresh, datetime) and last_refresh.tzinfo is None:
            last_refresh = last_refresh.replace(tzinfo=timezone.utc)
        return EnterpriseKnowledgeStatistics(
            total_documents=len(self._service_repository.all_documents()),
            documents_by_category=counts,
            faq_entries=len(self._service_repository.faq_answers()),
            knowledge_requests=metrics.knowledge_requests,
            knowledge_runtime_hits=metrics.hits,
            knowledge_runtime_misses=metrics.misses,
            knowledge_runtime_cache_hits=metrics.cache_hits,
            knowledge_runtime_reload_time_ms=metrics.reload_time_ms,
            knowledge_runtime_last_refresh=last_refresh,
            provider_distribution=metrics.provider_distribution,
            cache_hit_rate=metrics.cache_hit_rate,
            cache_size=metrics.cache_size,
            average_search_time_ms=metrics.average_search_time_ms,
            knowledge_sources=list(metrics.provider_distribution.keys()),
        )

    def get_health(self) -> EnterpriseKnowledgeHealthResponse:
        return build_health_response()

    def list_by_category(self, category: str):
        return self._service_repository.by_category(category)

    def all_documents(self):
        return list(self._service_repository.all_documents())
