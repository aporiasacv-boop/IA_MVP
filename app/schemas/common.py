from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class VersionResponse(BaseModel):
    name: str
    version: str


class UploadResponse(BaseModel):
    filename: str
    content_type: str | None
    size_bytes: int
    status: str
    message: str
