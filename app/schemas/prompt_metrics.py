from pydantic import BaseModel, ConfigDict, Field


class PromptMetrics(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "prompt_chars": 12458,
            "context_chars": 11800,
            "question_chars": 32,
            "response_chars": 180,
            "estimated_tokens": 3100,
            "sources_used": ["TOP_CLIENTES", "METADATA"],
        }
    })

    prompt_chars: int = 0
    context_chars: int = 0
    question_chars: int = 0
    response_chars: int = 0
    estimated_tokens: int = 0
    sources_used: list[str] = Field(default_factory=list)


class PromptAuditResult(BaseModel):
    metrics: PromptMetrics
    prompt_preview: str = Field(default="", description="Primeros 500 caracteres del prompt")
