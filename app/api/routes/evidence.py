from fastapi import APIRouter, Depends

from app.api.deps import get_evidence_package_service
from app.evidence_package.schemas import (
    EnterpriseEvidencePackage,
    EvidenceBuildRequest,
    EvidenceSchemaResponse,
    EvidenceStatisticsResponse,
)
from app.evidence_package.service import EvidencePackageService

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.post("/build", response_model=EnterpriseEvidencePackage)
def build_evidence_package(
    request: EvidenceBuildRequest,
    service: EvidencePackageService = Depends(get_evidence_package_service),
) -> EnterpriseEvidencePackage:
    return service.build(request)


@router.get("/schema", response_model=EvidenceSchemaResponse)
def get_evidence_schema(
    service: EvidencePackageService = Depends(get_evidence_package_service),
) -> EvidenceSchemaResponse:
    return service.get_schema()


@router.get("/statistics", response_model=EvidenceStatisticsResponse)
def get_evidence_statistics(
    service: EvidencePackageService = Depends(get_evidence_package_service),
) -> EvidenceStatisticsResponse:
    return service.get_statistics()


@router.get("/example", response_model=EnterpriseEvidencePackage)
def get_evidence_example(
    service: EvidencePackageService = Depends(get_evidence_package_service),
) -> EnterpriseEvidencePackage:
    return service.get_example()
