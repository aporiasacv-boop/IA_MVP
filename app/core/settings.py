from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "IA_MVP"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5433
    DATABASE_USER: str = "ia_mvp"
    DATABASE_PASSWORD: str = "ia_mvp"
    DATABASE_NAME: str = "ia_mvp"

    DATA_RAW_DIR: Path = Path("data/raw")
    DATA_PROCESSED_DIR: Path = Path("data/processed")

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"

    LLM_PROVIDER: str = "mock"
    LLM_FALLBACK_PROVIDER: str = ""
    LLM_TIMEOUT_SECONDS: float = 60.0
    EXECUTIVE_REASONING_ENABLED: bool = True
    CONVERSATION_RESPONSE_LLM_ENABLED: bool = True
    ENTERPRISE_REASONING_ENGINE_ENABLED: bool = True
    ENTERPRISE_PERSONALITY_ENABLED: bool = True
    EXECUTIVE_INSIGHT_ENABLED: bool = True
    BUSINESS_COPILOT_ENABLED: bool = True
    EXECUTIVE_ADVISOR_ENABLED: bool = True
    CAPABILITY_REASONING_AUDIT_ENABLED: bool = True
    CAPABILITY_REASONER_ENABLED: bool = True
    CAPABILITY_PLAN_EXECUTOR_ENABLED: bool = True
    ENTERPRISE_EVIDENCE_PLANNER_ENABLED: bool = True
    ENTERPRISE_EVIDENCE_ORCHESTRATOR_ENABLED: bool = True
    EXECUTIVE_REASONING_V2_ENABLED: bool = True

    REASONING_GOVERNANCE: bool = True
    REASONING_MIN_CONFIDENCE: float = 0.75
    REASONING_ROUTE_CONVERSATION: bool = True
    REASONING_ROUTE_INSTITUTIONAL: bool = True
    REASONING_ROUTE_CLARIFICATION: bool = True
    REASONING_ROUTE_BUSINESS: bool = False
    REASONING_ROUTE_EXECUTIVE: bool = False
    REASONING_ROUTE_LEGACY: bool = False

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    GPT_COST_PER_1K_TOKENS: float = 0.0
    GPT_COST_PER_1K_INPUT_TOKENS: float = 0.0025
    GPT_COST_PER_1K_OUTPUT_TOKENS: float = 0.01
    CLAUDE_COST_PER_1K_TOKENS: float = 0.0
    CLAUDE_COST_PER_1K_INPUT_TOKENS: float = 0.003
    CLAUDE_COST_PER_1K_OUTPUT_TOKENS: float = 0.015
    OLLAMA_COST_PER_1K_TOKENS: float = 0.0
    ESTIMATED_TOKENS_PER_LEGACY_CALL: float = 0.0
    ESTIMATED_TOKENS_PER_EXECUTIVE_CALL: float = 2500.0
    USD_TO_MXN_RATE: float = 17.5
    FINOPS_BASELINE_INPUT_TOKENS: float = 800.0
    FINOPS_BASELINE_OUTPUT_TOKENS: float = 400.0
    FINOPS_QUERIES_PER_USER_DAY: float = 12.0

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
