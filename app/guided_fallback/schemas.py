from pydantic import BaseModel, ConfigDict, Field

from app.suggested_questions.schemas import SuggestedQuestionsResult


class GuidedFallbackResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "answer": "Actualmente puedo ayudarte con:\n\n• Clientes\n• Proveedores",
            "fallback_type": "UNKNOWN",
            "suggested_questions": [
                "¿Cuántos clientes existen?",
                "¿Qué proveedor tuvo más movimiento en junio?",
            ],
            "metadata": {
                "fallback_success": True,
                "suggested_questions_count": 2,
            },
        }
    })

    success: bool
    answer: str
    fallback_type: str
    suggested_questions: list[str]
    suggestions: SuggestedQuestionsResult | None = None
    metadata: dict = Field(default_factory=dict)
