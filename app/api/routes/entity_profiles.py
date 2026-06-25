from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_business_entity_profile_service
from app.business_entity_profile.schemas import EntityProfileItem, EntityProfileListResponse, EntityProfileStatisticsResponse
from app.business_entity_profile.service import BusinessEntityProfileService

router = APIRouter(prefix="/api/entity-profiles", tags=["entity-profiles"])


@router.get("", response_model=EntityProfileListResponse)
def list_entity_profiles(
    search: str | None = Query(default=None, max_length=200),
    sort_by: str = Query(default="total_movements", max_length=50),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    service: BusinessEntityProfileService = Depends(get_business_entity_profile_service),
) -> EntityProfileListResponse:
    return service.list_profiles(
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )


@router.get("/statistics", response_model=EntityProfileStatisticsResponse)
def get_entity_profile_statistics(
    service: BusinessEntityProfileService = Depends(get_business_entity_profile_service),
) -> EntityProfileStatisticsResponse:
    return service.get_statistics()


@router.get("/{canonical_id}", response_model=EntityProfileItem)
def get_entity_profile(
    canonical_id: int,
    service: BusinessEntityProfileService = Depends(get_business_entity_profile_service),
) -> EntityProfileItem:
    profile = service.get_profile(canonical_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return profile
