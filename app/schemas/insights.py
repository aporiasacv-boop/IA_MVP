from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InsightResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "tipo": "concentracion_clientes",
            "categoria": "clientes",
            "severidad": "media",
            "titulo": "Concentracion en clientes principales",
            "mensaje": "Los 5 principales clientes representan el 64.46% del volumen registrado de clientes.",
            "valor": "64.4683",
            "fecha_generacion": "2026-06-18T12:00:00",
        }
    })

    tipo: str
    categoria: str
    severidad: str
    titulo: str
    mensaje: str
    valor: Decimal | int | str
    fecha_generacion: datetime


class InsightsResumenResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total_insights": 7,
            "criticos": 0,
            "altos": 1,
            "medios": 4,
            "bajos": 2,
        }
    })

    total_insights: int
    criticos: int = Field(description="Insights con severidad critica")
    altos: int = Field(description="Insights con severidad alta")
    medios: int = Field(description="Insights con severidad media")
    bajos: int = Field(description="Insights con severidad baja")
