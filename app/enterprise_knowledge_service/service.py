from datetime import datetime, timezone

from app.enterprise_knowledge_service.constants import CATEGORY_LABELS
from app.enterprise_knowledge_service.metrics import get_enterprise_knowledge_metrics
from app.enterprise_knowledge_service.providers.base import PLANNED_PROVIDER_TYPES
from app.enterprise_knowledge_service.providers.knowledge_pack import KnowledgePackProvider
from app.enterprise_knowledge_service.repository.repository import KnowledgeRepository
from app.enterprise_knowledge_service.schemas import (
    BusinessContextRequest,
    BusinessContextResponse,
    CapabilitiesPayload,
    EnterpriseKnowledgeHealthResponse,
    EnterpriseKnowledgeStatistics,
    KnowledgeCategoriesResponse,
    KnowledgeCategorySummary,
    KnowledgeDocument,
    KnowledgeProviderInfo,
    KnowledgeProvidersResponse,
    KnowledgeSearchResult,
)
from app.enterprise_knowledge_service.search.engine import KnowledgeSearchEngine


class EnterpriseKnowledgePlatformService:
    """Servicio transversal de conocimiento empresarial (EKS)."""

    def __init__(
        self,
        repository: KnowledgeRepository | None = None,
        search_engine: KnowledgeSearchEngine | None = None,
    ) -> None:
        self._repository = repository or KnowledgeRepository()
        self._search = search_engine or KnowledgeSearchEngine(self._repository)
        self._pack_provider = KnowledgePackProvider()

    def search(self, query: str, *, limit: int = 50) -> KnowledgeSearchResult:
        return self._search.search(query, limit=limit)

    def get_concept(self, concept_id: str) -> KnowledgeDocument | None:
        doc = self._repository.by_id(concept_id)
        if doc is None or doc.category != "concepts":
            return None
        return doc

    def get_rule(self, rule_id: str) -> KnowledgeDocument | None:
        doc = self._repository.by_id(rule_id)
        if doc is None or doc.category != "rules":
            return None
        return doc

    def get_faq(self, question: str) -> str | None:
        key = question.strip()
        answers = self._repository.faq_answers()
        from app.utils.text_normalizer import normalize_for_matching

        normalized = normalize_for_matching(key)
        return answers.get(normalized)

    def get_glossary(self, term_id: str | None = None) -> list[KnowledgeDocument]:
        items = self._repository.by_category("glossary")
        if term_id is None:
            return items
        return [doc for doc in items if doc.id == term_id]

    def get_examples(self) -> list[KnowledgeDocument]:
        return self._repository.by_category("examples")

    def get_executive_context(self) -> list[KnowledgeDocument]:
        return self._repository.by_category("executive")

    def get_capabilities(self) -> CapabilitiesPayload:
        capabilities = list(self._repository.capabilities())
        examples = list(self._repository.examples())
        lines = [self._repository.intro_line(), ""]
        for item in capabilities:
            lines.append(f"• {item}")
        if examples:
            lines.extend(["", self._repository.examples_line()])
            for example in examples:
                lines.append(f"• {example}")
        return CapabilitiesPayload(
            answer="\n".join(lines),
            capabilities=capabilities,
            examples=examples,
        )

    def exists(self, doc_id: str) -> bool:
        return self._repository.exists(doc_id)

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

    def get_business_context(self, request: BusinessContextRequest) -> BusinessContextResponse:
        """Punto de extensión para EEP: contexto de negocio sin exponer el origen."""
        resolved = self.search(request.question, limit=3)
        if not resolved.items:
            return BusinessContextResponse(
                available=False,
                summary="",
                sources=[],
            )
        summary_parts = [item.title for item in resolved.items[:3]]
        return BusinessContextResponse(
            available=True,
            summary="; ".join(summary_parts),
            sources=[item.path for item in resolved.items[:3]],
        )

    def get_statistics(self) -> EnterpriseKnowledgeStatistics:
        counts: dict[str, int] = {}
        for doc in self._repository.all_documents():
            counts[doc.category] = counts.get(doc.category, 0) + 1
        metrics = get_enterprise_knowledge_metrics()
        metrics.set_provider_distribution(self._repository.provider_distribution())
        last_refresh = metrics.last_refresh
        if isinstance(last_refresh, datetime) and last_refresh.tzinfo is None:
            last_refresh = last_refresh.replace(tzinfo=timezone.utc)
        return EnterpriseKnowledgeStatistics(
            total_documents=len(self._repository.all_documents()),
            documents_by_category=counts,
            faq_entries=len(self._repository.faq_answers()),
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

    def get_providers(self) -> KnowledgeProvidersResponse:
        active = [
            KnowledgeProviderInfo(
                id=self._pack_provider.provider_id,
                name=self._pack_provider.display_name,
                status="active" if self._pack_provider.is_available() else "unavailable",
                document_count=len(self._repository.all_documents()),
            )
        ]
        planned = [
            KnowledgeProviderInfo(
                id=provider_type.provider_id,
                name=provider_type.display_name,
                status="planned",
                document_count=0,
            )
            for provider_type in PLANNED_PROVIDER_TYPES
        ]
        return KnowledgeProvidersResponse(active=active, planned=planned)

    def get_health(self) -> EnterpriseKnowledgeHealthResponse:
        from app.enterprise_knowledge_service.health import build_health_response

        return build_health_response()

    def invalidate_cache(self) -> None:
        self._repository.invalidate()


_service: EnterpriseKnowledgePlatformService | None = None


def get_enterprise_knowledge_platform_service() -> EnterpriseKnowledgePlatformService:
    global _service
    if _service is None:
        _service = EnterpriseKnowledgePlatformService()
    return _service


def reset_enterprise_knowledge_platform_service() -> None:
    global _service
    _service = None


# Alias público solicitado por arquitectura EKS
EnterpriseKnowledgeService = EnterpriseKnowledgePlatformService
get_enterprise_knowledge_service = get_enterprise_knowledge_platform_service
