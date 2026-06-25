from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation


class BusinessFilters(BaseModel):
    cliente_codigo: str | None = None
    proveedor_codigo: str | None = None
    cuenta_codigo: str | None = None
    mes: int | None = None
    anio: int | None = None


class BusinessSemanticIntent(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "operation": "MAX",
            "target_entity": "TRANSACCION",
            "source_entity": "CLIENTE",
            "filters": {
                "cliente_codigo": "C001",
                "proveedor_codigo": None,
                "cuenta_codigo": None,
                "mes": None,
                "anio": None,
            },
            "confidence": 0.95,
            "source_question": "¿Cuál fue la transacción más alta del cliente C001?",
        }
    })

    operation: BusinessOperation | None = None
    target_entity: BusinessEntity | None = None
    source_entity: BusinessEntity | None = None
    filters: BusinessFilters = Field(default_factory=BusinessFilters)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_question: str = ""
