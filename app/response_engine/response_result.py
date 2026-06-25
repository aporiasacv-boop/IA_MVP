from pydantic import BaseModel, ConfigDict, Field

from app.suggested_questions.schemas import SuggestedQuestionsResult


class BusinessResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "answer": "Actualmente existen 50 clientes registrados.",
            "query_type": "COUNT_CLIENTES",
            "metadata": {},
        }
    })

    success: bool
    answer: str
    query_type: str
    metadata: dict = Field(default_factory=dict)
    suggestions: "SuggestedQuestionsResult | None" = None
