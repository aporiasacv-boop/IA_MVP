from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_enterprise_reasoning_service
from app.enterprise_reasoning.schemas import (
    EnterpriseReasoningObjectSchema,
    ReasoningObjectListResponse,
    ReasoningRulesResponse,
    ReasoningStatisticsResponse,
)
from app.enterprise_reasoning.service import EnterpriseReasoningService

router = APIRouter(prefix="/api/reasoning", tags=["reasoning"])


@router.get("/entities", response_model=ReasoningObjectListResponse)
def list_reasoning_entities(
    search: str | None = Query(default=None, max_length=200),
    sort_by: str = Query(default="average_confidence", max_length=50),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    service: EnterpriseReasoningService = Depends(get_enterprise_reasoning_service),
) -> ReasoningObjectListResponse:
    return service.list_entities(
        search=search, sort_by=sort_by, sort_dir=sort_dir, page=page, page_size=page_size
    )


@router.get("/statistics", response_model=ReasoningStatisticsResponse)
def get_reasoning_statistics(
    service: EnterpriseReasoningService = Depends(get_enterprise_reasoning_service),
) -> ReasoningStatisticsResponse:
    return service.get_statistics()


@router.get("/rules", response_model=ReasoningRulesResponse)
def get_reasoning_rules(
    service: EnterpriseReasoningService = Depends(get_enterprise_reasoning_service),
) -> ReasoningRulesResponse:
    return service.get_rules()


@router.get("/entities/{canonical_id}", response_model=EnterpriseReasoningObjectSchema)
def get_reasoning_entity(
    canonical_id: int,
    service: EnterpriseReasoningService = Depends(get_enterprise_reasoning_service),
) -> EnterpriseReasoningObjectSchema:
    obj = service.get_entity(canonical_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Objeto de razonamiento no encontrado")
    return obj
