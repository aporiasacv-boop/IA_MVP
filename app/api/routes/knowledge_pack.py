from fastapi import APIRouter, Depends, Query

from app.api.deps import get_business_knowledge_pack_service
from app.knowledge_pack.schemas import KnowledgePackListResponse, KnowledgePackSearchResponse
from app.knowledge_pack.service import BusinessKnowledgePackService

router = APIRouter(prefix="/api/knowledge-pack", tags=["knowledge-pack"])


@router.get("/concepts", response_model=KnowledgePackListResponse)
def list_concepts(
    service: BusinessKnowledgePackService = Depends(get_business_knowledge_pack_service),
) -> KnowledgePackListResponse:
    return service.list_concepts()


@router.get("/glossary", response_model=KnowledgePackListResponse)
def list_glossary(
    service: BusinessKnowledgePackService = Depends(get_business_knowledge_pack_service),
) -> KnowledgePackListResponse:
    return service.list_glossary()


@router.get("/faq", response_model=KnowledgePackListResponse)
def list_faq(
    service: BusinessKnowledgePackService = Depends(get_business_knowledge_pack_service),
) -> KnowledgePackListResponse:
    return service.list_faq()


@router.get("/rules", response_model=KnowledgePackListResponse)
def list_rules(
    service: BusinessKnowledgePackService = Depends(get_business_knowledge_pack_service),
) -> KnowledgePackListResponse:
    return service.list_rules()


@router.get("/scenarios", response_model=KnowledgePackListResponse)
def list_scenarios(
    service: BusinessKnowledgePackService = Depends(get_business_knowledge_pack_service),
) -> KnowledgePackListResponse:
    return service.list_scenarios()


@router.get("/search", response_model=KnowledgePackSearchResponse)
def search_knowledge_pack(
    q: str = Query(min_length=1, max_length=200),
    service: BusinessKnowledgePackService = Depends(get_business_knowledge_pack_service),
) -> KnowledgePackSearchResponse:
    return service.search(q)
