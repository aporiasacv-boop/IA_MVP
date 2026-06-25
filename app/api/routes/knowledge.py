from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_enterprise_knowledge_service
from app.enterprise_knowledge.schemas import (
    EnterpriseKnowledgeObjectSchema,
    KnowledgeObjectListResponse,
    KnowledgeSchemaResponse,
    KnowledgeStatisticsResponse,
)
from app.enterprise_knowledge.service import EnterpriseKnowledgeService

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/entities", response_model=KnowledgeObjectListResponse)
def list_knowledge_entities(
    search: str | None = Query(default=None, max_length=200),
    sort_by: str = Query(default="completeness", max_length=50),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    service: EnterpriseKnowledgeService = Depends(get_enterprise_knowledge_service),
) -> KnowledgeObjectListResponse:
    return service.list_entities(
        search=search, sort_by=sort_by, sort_dir=sort_dir, page=page, page_size=page_size
    )


@router.get("/statistics", response_model=KnowledgeStatisticsResponse)
def get_knowledge_statistics(
    service: EnterpriseKnowledgeService = Depends(get_enterprise_knowledge_service),
) -> KnowledgeStatisticsResponse:
    return service.get_statistics()


@router.get("/schema", response_model=KnowledgeSchemaResponse)
def get_knowledge_schema(
    service: EnterpriseKnowledgeService = Depends(get_enterprise_knowledge_service),
) -> KnowledgeSchemaResponse:
    return service.get_schema()


@router.get("/entities/{canonical_id}", response_model=EnterpriseKnowledgeObjectSchema)
def get_knowledge_entity(
    canonical_id: int,
    service: EnterpriseKnowledgeService = Depends(get_enterprise_knowledge_service),
) -> EnterpriseKnowledgeObjectSchema:
    obj = service.get_entity(canonical_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Objeto de conocimiento no encontrado")
    return obj
