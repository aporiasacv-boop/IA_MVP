from fastapi import APIRouter

from app.core.settings import settings
from app.schemas.common import VersionResponse

router = APIRouter()


@router.get("/version", response_model=VersionResponse)
async def get_version() -> VersionResponse:
    return VersionResponse(name=settings.APP_NAME, version=settings.APP_VERSION)
