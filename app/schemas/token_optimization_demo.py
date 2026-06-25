from pydantic import BaseModel, ConfigDict, Field


class SimpleQuestionDemo(BaseModel):
    question: str
    tokens_if_llm: int
    tokens_actual: int
    saving_percent: int


class ExecutiveQuestionDemo(BaseModel):
    question: str
    real_prompt_tokens: int
    llm_time_ms: int


class TokenOptimizationDemo(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "simple_question": {
                "question": "¿Qué KPIs tienes?",
                "tokens_if_llm": 800,
                "tokens_actual": 0,
                "saving_percent": 100,
            },
            "executive_question": {
                "question": "¿De qué insights hablas?",
                "real_prompt_tokens": 1228,
                "llm_time_ms": 52000,
            },
        }
    })

    simple_question: SimpleQuestionDemo
    executive_question: ExecutiveQuestionDemo
