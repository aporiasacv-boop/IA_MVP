from pydantic import BaseModel, ConfigDict, Field


class SuggestedQuestionsResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "questions": [
                "¿Cuántos proveedores existen?",
                "Muéstrame los principales clientes",
                "¿Cuál es el periodo de los datos?",
            ],
            "source": "type_rules",
            "confidence": 0.9,
            "metadata": {
                "suggested_questions_count": 3,
                "query_type": "COUNT_CLIENTES",
            },
        }
    })

    questions: list[str]
    source: str
    confidence: float
    metadata: dict = Field(default_factory=dict)
