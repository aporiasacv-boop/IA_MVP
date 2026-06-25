from pydantic import BaseModel, ConfigDict, Field


class MetadataResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "fecha_minima": "2025-01-01",
            "fecha_maxima": "2025-12-31",
            "registros": 386480,
            "clientes": 50,
            "proveedores": 766,
            "cuentas": 1962,
            "anios": [2025],
            "meses": 12,
        }
    })

    fecha_minima: str
    fecha_maxima: str
    registros: int
    clientes: int
    proveedores: int
    cuentas: int
    anios: list[int]
    meses: int = Field(description="Cantidad de periodos mensuales disponibles")
