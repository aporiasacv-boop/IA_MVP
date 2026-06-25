from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.settings import settings

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}


class UploadService:
    def __init__(self, raw_dir: Path | None = None) -> None:
        self.raw_dir = raw_dir or settings.DATA_RAW_DIR

    def validate_excel_file(self, file: UploadFile) -> None:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        extension = Path(file.filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Excel files (.xlsx, .xls) are allowed",
            )

        if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type for Excel file",
            )

    async def save_raw_file(self, file: UploadFile) -> tuple[str, int]:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        destination = self.raw_dir / Path(file.filename).name
        content = await file.read()
        destination.write_bytes(content)
        return destination.name, len(content)
