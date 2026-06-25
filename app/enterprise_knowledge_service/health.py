from datetime import datetime, timezone

from app.enterprise_knowledge_service.metrics import get_enterprise_knowledge_metrics
from app.enterprise_knowledge_service.providers.knowledge_pack import PACK_ROOT
from app.enterprise_knowledge_service.repository.repository import KnowledgeRepository
from app.enterprise_knowledge_service.schemas import EnterpriseKnowledgeHealthResponse


def build_health_response() -> EnterpriseKnowledgeHealthResponse:
    repository = KnowledgeRepository()
    metrics = get_enterprise_knowledge_metrics()
    documents = repository.all_documents()
    metrics.set_provider_distribution(repository.provider_distribution())
    last_refresh = metrics.last_refresh
    if isinstance(last_refresh, datetime) and last_refresh.tzinfo is None:
        last_refresh = last_refresh.replace(tzinfo=timezone.utc)
    return EnterpriseKnowledgeHealthResponse(
        status="ok" if documents else "degraded",
        cache_valid=bool(documents),
        total_documents=len(documents),
        cache_size=metrics.cache_size or len(documents),
        cache_hit_rate=metrics.cache_hit_rate,
        last_refresh=last_refresh,
        reload_time_ms=metrics.reload_time_ms,
        active_providers=["knowledge_pack"] if PACK_ROOT.exists() else [],
    )
