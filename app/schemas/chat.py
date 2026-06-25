from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.entities import ExtractedEntities
from app.schemas.prompt_metrics import PromptMetrics
from app.schemas.response_mode import ResponseMode
from app.schemas.timings import ChatTimings
from app.schemas.token_optimization_demo import TokenOptimizationDemo


class ChatRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"question": "Quien es nuestro mejor cliente?"}
    })

    question: str = Field(min_length=1, description="Pregunta en lenguaje natural")


class ChatResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "intent": "TOP_CLIENTES",
            "answer": (
                "Durante 2025 el cliente con mayor actividad fue PUBLICO EN GENERAL "
                "con 57,730 movimientos registrados."
            ),
            "data": [
                {
                    "ranking": 1,
                    "cliente_codigo": "C0003",
                    "cliente_nombre": "PUBLICO EN GENERAL",
                    "movimientos": 57730,
                }
            ],
        }
    })

    intent: str
    intent_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    response_mode: ResponseMode = ResponseMode.GENERATIVE
    answer: str
    data: Any
    original_question: str = ""
    normalized_question: str = ""
    corrections_applied: list[str] = Field(default_factory=list)
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    sources: list[str] = Field(default_factory=list)
    timings: ChatTimings = Field(default_factory=ChatTimings)
    prompt_metrics: PromptMetrics = Field(default_factory=PromptMetrics)
    token_optimization_demo: TokenOptimizationDemo | None = None
