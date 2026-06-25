from fastapi import APIRouter, Depends, Query

from app.api.deps import get_business_knowledge_runtime
from app.business_knowledge.runtime import BusinessKnowledgeRuntime
from app.business_knowledge.schemas import (
    KnowledgeCategoriesResponse,
    KnowledgeRuntimeHealthResponse,
    KnowledgeRuntimeStatistics,
    KnowledgeSearchResult,
)

router = APIRouter(prefix="/api/business-knowledge", tags=["business-knowledge"])


@router.get("/health", response_model=KnowledgeRuntimeHealthResponse)
def business_knowledge_health(
    runtime: BusinessKnowledgeRuntime = Depends(get_business_knowledge_runtime),
) -> KnowledgeRuntimeHealthResponse:
    return runtime.get_health()


@router.get("/statistics", response_model=KnowledgeRuntimeStatistics)
def business_knowledge_statistics(
    runtime: BusinessKnowledgeRuntime = Depends(get_business_knowledge_runtime),
) -> KnowledgeRuntimeStatistics:
    return runtime.get_statistics()


@router.get("/search", response_model=KnowledgeSearchResult)
def business_knowledge_search(
    q: str = Query(min_length=1, max_length=500),
    runtime: BusinessKnowledgeRuntime = Depends(get_business_knowledge_runtime),
) -> KnowledgeSearchResult:
    return runtime.search(q)


@router.get("/categories", response_model=KnowledgeCategoriesResponse)
def business_knowledge_categories(
    runtime: BusinessKnowledgeRuntime = Depends(get_business_knowledge_runtime),
) -> KnowledgeCategoriesResponse:
    return runtime.list_categories()
