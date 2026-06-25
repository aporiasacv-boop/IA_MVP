from fastapi import APIRouter, Depends

from app.api.deps import get_metadata_service
from app.schemas.metadata import MetadataResponse
from app.services.metadata_service import MetadataService

router = APIRouter(prefix="/api", tags=["metadata"])


@router.get(
    "/metadata",
    response_model=MetadataResponse,
    summary="Metadata empresarial del dataset",
    description=(
        "Devuelve periodo disponible, volumenes agregados y cobertura temporal "
        "calculados desde fact tables y materialized views."
    ),
)
def get_metadata(
    service: MetadataService = Depends(get_metadata_service),
) -> MetadataResponse:
    return MetadataResponse(**service.get_dataset_summary())
