from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import BusinessEntity


class EntityResolution(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "entities": ["CLIENTE", "CUENTA"],
            "parameters": {"codigo": "IMA0709183"},
            "confidence": 1.0,
            "matched_terms": ["cliente", "cuenta"],
        }
    })

    entities: list[BusinessEntity] = Field(
        default_factory=list,
        description="Entidades empresariales detectadas en la pregunta",
    )
    parameters: dict = Field(
        default_factory=dict,
        description="Parametros extraidos (mes, anio, codigo)",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Proporcion de entidades detectadas sobre entidades posibles",
    )
    matched_terms: list[str] = Field(
        default_factory=list,
        description="Terminos del catalogo que coincidieron",
    )
