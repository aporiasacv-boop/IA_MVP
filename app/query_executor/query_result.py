from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BusinessQueryResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "query_type": "COUNT_CLIENTES",
            "success": True,
            "data": {"total": 50},
            "metadata": {"filters": {}},
        }
    })

    query_type: str
    success: bool
    data: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
