from fastapi import APIRouter, Depends, Query

from app.api.deps import get_canonical_business_entity_service
from app.canonical_business_entity.schemas import (
    CanonicalEntityListResponse,
    CanonicalStatisticsResponse,
    CanonicalSuggestionListResponse,
)
from app.canonical_business_entity.service import CanonicalBusinessEntityService

router = APIRouter(prefix="/api/canonical-entities", tags=["canonical-entities"])


@router.get("", response_model=CanonicalEntityListResponse)
def list_canonical_entities(
    search: str | None = Query(default=None, max_length=200),
    sort_by: str = Query(default="alias_count", max_length=50),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    service: CanonicalBusinessEntityService = Depends(get_canonical_business_entity_service),
) -> CanonicalEntityListResponse:
    return service.list_canonical(
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )


@router.get("/suggestions", response_model=CanonicalSuggestionListResponse)
def list_canonical_suggestions(
    status: str | None = Query(default="pending", max_length=20),
    min_score: float | None = Query(default=None, ge=0, le=1),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    service: CanonicalBusinessEntityService = Depends(get_canonical_business_entity_service),
) -> CanonicalSuggestionListResponse:
    return service.list_suggestions(
        status=status,
        min_score=min_score,
        page=page,
        page_size=page_size,
        sort_dir=sort_dir,
    )


@router.get("/statistics", response_model=CanonicalStatisticsResponse)
def get_canonical_statistics(
    service: CanonicalBusinessEntityService = Depends(get_canonical_business_entity_service),
) -> CanonicalStatisticsResponse:
    return service.get_statistics()
