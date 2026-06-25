from pydantic import BaseModel, ConfigDict, Field

from app.domain.operations import BusinessOperation


class OperationResolution(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "operation": "COUNT",
            "confidence": 1.0,
            "matched_terms": ["cuantos", "existen"],
        }
    })

    operation: BusinessOperation | None = Field(
        default=None,
        description="Operacion empresarial detectada en la pregunta",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Proporcion de coincidencias atribuidas a la operacion ganadora",
    )
    matched_terms: list[str] = Field(
        default_factory=list,
        description="Terminos del catalogo que coincidieron para la operacion detectada",
    )
