import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class PerformanceMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: str
    question: str
    handled_by: str
    operation_time_ms: float | None = None
    entity_time_ms: float | None = None
    intent_time_ms: float | None = None
    planner_time_ms: float | None = None
    executor_time_ms: float | None = None
    database_time_ms: float | None = None
    response_time_ms: float | None = None
    legacy_chat_time_ms: float | None = None
    ollama_time_ms: float | None = None
    total_time_ms: float
    query_type: str | None = None
    success: bool
    suggested_questions_count: int | None = None
    route_type: str | None = None
    response_success: bool | None = None
    deterministic_resolution: bool | None = None
    used_ai: bool | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PerformanceCollector:
    question: str
    request_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: float = field(default_factory=time.perf_counter)
    operation_time_ms: float | None = None
    entity_time_ms: float | None = None
    intent_time_ms: float | None = None
    planner_time_ms: float | None = None
    executor_time_ms: float | None = None
    database_time_ms: float | None = None
    response_time_ms: float | None = None
    legacy_chat_time_ms: float | None = None
    ollama_time_ms: float | None = None
    handled_by: str | None = None
    query_type: str | None = None
    success: bool = False
    suggested_questions_count: int | None = None

    def record_stage(self, stage: str, duration_ms: float) -> None:
        stage_fields = {
            "operation": "operation_time_ms",
            "entity": "entity_time_ms",
            "intent": "intent_time_ms",
            "planner": "planner_time_ms",
            "executor": "executor_time_ms",
            "response": "response_time_ms",
            "legacy_chat": "legacy_chat_time_ms",
            "ollama": "ollama_time_ms",
        }
        field_name = stage_fields.get(stage)
        if field_name is not None:
            setattr(self, field_name, duration_ms)

    def finalize(
        self,
        *,
        handled_by: str,
        success: bool,
        query_type: str | None,
        database_time_ms: float | None,
        suggested_questions_count: int | None = None,
    ) -> PerformanceMetrics:
        total_time_ms = round((time.perf_counter() - self.started_at) * 1000, 4)
        used_ai = handled_by == "legacy_chat"
        return PerformanceMetrics(
            request_id=self.request_id,
            question=self.question,
            handled_by=handled_by,
            operation_time_ms=self.operation_time_ms,
            entity_time_ms=self.entity_time_ms,
            intent_time_ms=self.intent_time_ms,
            planner_time_ms=self.planner_time_ms,
            executor_time_ms=self.executor_time_ms,
            database_time_ms=database_time_ms,
            response_time_ms=self.response_time_ms,
            legacy_chat_time_ms=self.legacy_chat_time_ms,
            ollama_time_ms=self.ollama_time_ms,
            total_time_ms=total_time_ms,
            query_type=query_type,
            success=success,
            suggested_questions_count=suggested_questions_count,
            route_type=handled_by,
            response_success=success,
            deterministic_resolution=not used_ai,
            used_ai=used_ai,
            created_at=datetime.now(timezone.utc),
        )


_active_collector: ContextVar[PerformanceCollector | None] = ContextVar(
    "active_performance_collector",
    default=None,
)

_db_time_ms: ContextVar[float] = ContextVar("database_time_ms", default=0.0)


def get_active_collector() -> PerformanceCollector | None:
    return _active_collector.get()


def set_active_collector(collector: PerformanceCollector | None) -> None:
    _active_collector.set(collector)


def reset_database_time() -> None:
    _db_time_ms.set(0.0)


def add_database_time(duration_ms: float) -> None:
    _db_time_ms.set(round(_db_time_ms.get() + duration_ms, 4))


def get_database_time() -> float:
    return _db_time_ms.get()


def elapsed_ms(started_at: float) -> float:
    return round((time.perf_counter() - started_at) * 1000, 4)
