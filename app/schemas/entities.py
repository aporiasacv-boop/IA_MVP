from pydantic import BaseModel, ConfigDict, Field


class ExtractedEntities(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "month": 6,
            "year": 2025,
            "client_code": "C0003",
            "account_code": None,
            "period": None,
        }
    })

    month: int | None = Field(default=None, ge=1, le=12)
    year: int | None = Field(default=None)
    client_code: str | None = None
    account_code: str | None = None
    period: str | None = Field(
        default=None,
        description="current_year | last_year | current_month | last_month",
    )
