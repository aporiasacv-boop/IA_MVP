from fastapi import APIRouter, File, UploadFile

from app.schemas.common import UploadResponse
from app.services.upload_service import UploadService

router = APIRouter()
upload_service = UploadService()


@router.post("", response_model=UploadResponse)
async def upload_excel(file: UploadFile = File(...)) -> UploadResponse:
    upload_service.validate_excel_file(file)
    filename, size_bytes = await upload_service.save_raw_file(file)
    return UploadResponse(
        filename=filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
        status="received",
        message="File stored successfully. Processing will be implemented in a future iteration.",
    )
