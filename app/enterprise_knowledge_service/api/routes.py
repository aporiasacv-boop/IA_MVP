from fastapi import APIRouter, Depends, Query

from app.api.deps import get_enterprise_knowledge_platform_service_dep
from app.enterprise_knowledge_service.schemas import (
    EnterpriseKnowledgeHealthResponse,
    EnterpriseKnowledgeStatistics,
    KnowledgeProvidersResponse,
    KnowledgeSearchResult,
)
from app.enterprise_knowledge_service.service import EnterpriseKnowledgePlatformService

router = APIRouter(prefix="/api/enterprise-knowledge", tags=["enterprise-knowledge"])


@router.get("/health", response_model=EnterpriseKnowledgeHealthResponse)
def enterprise_knowledge_health(
    service: EnterpriseKnowledgePlatformService = Depends(get_enterprise_knowledge_platform_service_dep),
) -> EnterpriseKnowledgeHealthResponse:
    return service.get_health()


@router.get("/statistics", response_model=EnterpriseKnowledgeStatistics)
def enterprise_knowledge_statistics(
    service: EnterpriseKnowledgePlatformService = Depends(get_enterprise_knowledge_platform_service_dep),
) -> EnterpriseKnowledgeStatistics:
    return service.get_statistics()


@router.get("/providers", response_model=KnowledgeProvidersResponse)
def enterprise_knowledge_providers(
    service: EnterpriseKnowledgePlatformService = Depends(get_enterprise_knowledge_platform_service_dep),
) -> KnowledgeProvidersResponse:
    return service.get_providers()


@router.get("/search", response_model=KnowledgeSearchResult)
def enterprise_knowledge_search(
    q: str = Query(min_length=1, max_length=500),
    service: EnterpriseKnowledgePlatformService = Depends(get_enterprise_knowledge_platform_service_dep),
) -> KnowledgeSearchResult:
    return service.search(q)
