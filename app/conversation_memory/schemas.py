from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class ConversationContext(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "session_id": "sess-abc123",
            "last_query_type": "COUNT_CLIENTES",
            "last_operation": "COUNT",
            "last_target_entity": "CLIENTE",
            "last_filters": {},
            "pending_clarification": None,
            "turn_count": 1,
            "created_at": "2026-06-23T12:00:00Z",
            "updated_at": "2026-06-23T12:00:00Z",
        }
    })

    session_id: str
    last_query_type: str | None = None
    last_operation: str | None = None
    last_target_entity: str | None = None
    last_filters: dict = Field(default_factory=dict)
    pending_clarification: dict | None = None
    turn_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
