from pydantic import BaseModel, ConfigDict, Field

from app.suggested_questions.schemas import SuggestedQuestionsResult


class HybridChatRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"message": "¿Cuántos clientes existen?"},
    })

    message: str = Field(min_length=1, description="Mensaje del usuario en lenguaje natural")
    session_id: str | None = Field(
        default=None,
        description="Identificador de sesión conversacional para memoria v1 en proceso",
    )


class HybridChatResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "handled_by": "business_pipeline",
            "success": True,
            "answer": "Actualmente existen 50 clientes registrados.",
            "metadata": {
                "handled_by": "business_pipeline",
                "query_type": "COUNT_CLIENTES",
                "confidence": 1.0,
            },
        }
    })

    handled_by: str
    success: bool
    answer: str
    suggestions: SuggestedQuestionsResult | None = None
    metadata: dict = Field(default_factory=dict)
