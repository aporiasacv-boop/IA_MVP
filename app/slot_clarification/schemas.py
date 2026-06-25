from pydantic import BaseModel, ConfigDict, Field


class SlotClarificationResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "answer": "¿De qué cliente deseas consultar la información?",
            "pending_query_type": "MAX_TRANSACCION_CLIENTE",
            "missing_slots": ["cliente_codigo"],
            "session_token": "a1b2c3d4e5f6",
            "metadata": {
                "clarification_type": "missing_slot",
                "confidence": 0.92,
            },
        }
    })

    success: bool
    answer: str
    pending_query_type: str
    missing_slots: list[str]
    session_token: str
    metadata: dict = Field(default_factory=dict)
