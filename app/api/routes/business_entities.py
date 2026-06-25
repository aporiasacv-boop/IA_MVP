from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_business_entity_master_service
from app.business_entity_master.schemas import (
    BusinessEntityItem,
    BusinessEntityListResponse,
    BusinessEntityStatisticsResponse,
)
from app.business_entity_master.service import BusinessEntityMasterService

router = APIRouter(prefix="/api/business-entities", tags=["business-entities"])


@router.get("", response_model=BusinessEntityListResponse)
def list_business_entities(
    search: str | None = Query(default=None, max_length=200),
    source_column: str | None = Query(default=None, max_length=100),
    classification_status: str | None = Query(default=None, max_length=30),
    sort_by: str = Query(default="movement_count", max_length=50),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    service: BusinessEntityMasterService = Depends(get_business_entity_master_service),
) -> BusinessEntityListResponse:
    return service.list_entities(
        search=search,
        source_column=source_column,
        classification_status=classification_status,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )


@router.get("/statistics", response_model=BusinessEntityStatisticsResponse)
def get_business_entity_statistics(
    service: BusinessEntityMasterService = Depends(get_business_entity_master_service),
) -> BusinessEntityStatisticsResponse:
    return service.get_statistics()


@router.get("/{entity_code}", response_model=list[BusinessEntityItem])
def get_business_entity_by_code(
    entity_code: str,
    source_column: str | None = Query(default=None, max_length=100),
    service: BusinessEntityMasterService = Depends(get_business_entity_master_service),
) -> list[BusinessEntityItem]:
    items = service.get_by_code(entity_code, source_column=source_column)
    if not items:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    return items
