from pydantic import BaseModel, ConfigDict, Field

from app.query_engine.query_types import BusinessQueryType


class BusinessQuery(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "query_type": "MAX_TRANSACCION_CLIENTE",
            "filters": {"cliente_codigo": "C001"},
        }
    })

    query_type: BusinessQueryType
    filters: dict = Field(default_factory=dict)
