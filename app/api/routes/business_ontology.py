from fastapi import APIRouter, Depends, Query

from app.api.deps import get_business_ontology_service
from app.business_ontology.schemas import (
    OntologyAssignmentListResponse,
    OntologyListResponse,
    OntologyStatisticsResponse,
    OntologyTypeListResponse,
)
from app.business_ontology.service import BusinessOntologyService

router = APIRouter(prefix="/api/business-ontology", tags=["business-ontology"])


@router.get("", response_model=OntologyListResponse)
def list_business_ontology(
    search: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    service: BusinessOntologyService = Depends(get_business_ontology_service),
) -> OntologyListResponse:
    return service.list_ontology(search=search, page=page, page_size=page_size)


@router.get("/types", response_model=OntologyTypeListResponse)
def list_ontology_types(
    concept_category: str | None = Query(default=None, max_length=20),
    service: BusinessOntologyService = Depends(get_business_ontology_service),
) -> OntologyTypeListResponse:
    return service.list_types(concept_category=concept_category)


@router.get("/assignments", response_model=OntologyAssignmentListResponse)
def list_ontology_assignments(
    status: str | None = Query(default="pending", max_length=20),
    concept_category: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    service: BusinessOntologyService = Depends(get_business_ontology_service),
) -> OntologyAssignmentListResponse:
    return service.list_assignments(
        status=status,
        concept_category=concept_category,
        page=page,
        page_size=page_size,
    )


@router.get("/statistics", response_model=OntologyStatisticsResponse)
def get_ontology_statistics(
    service: BusinessOntologyService = Depends(get_business_ontology_service),
) -> OntologyStatisticsResponse:
    return service.get_statistics()
