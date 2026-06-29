from pydantic import BaseModel, Field


class ReasoningDecision(BaseModel):
    """Decisión de enrutamiento del Enterprise Reasoning Engine (solo clasificación)."""

    intent: str = Field(description="Intención global detectada")
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_route: str = Field(description="Flujo recomendado")
    explanation: str = Field(description="Justificación breve de la clasificación")
    provider: str = ""
    model: str = ""
    reasoning_time_ms: float = 0.0
    source: str = "llm"

    def to_metadata(self) -> dict:
        return {
            "reasoning_intent": self.intent,
            "reasoning_confidence": round(self.confidence, 4),
            "reasoning_route": self.recommended_route,
            "reasoning_explanation": self.explanation,
            "reasoning_time_ms": round(self.reasoning_time_ms, 2),
            "reasoning_provider": self.provider,
            "reasoning_model": self.model,
            "reasoning_source": self.source,
        }


class ReasoningObservation(BaseModel):
    """Comparación entre decisión del motor y flujo realmente ejecutado."""

    recommended_route: str
    actual_route: str
    route_match: bool

    def to_metadata(self) -> dict:
        return {
            "reasoning_actual_route": self.actual_route,
            "reasoning_route_match": self.route_match,
        }
