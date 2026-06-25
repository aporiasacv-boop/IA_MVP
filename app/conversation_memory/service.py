from datetime import datetime, timezone
from dataclasses import dataclass

from app.conversation_memory.schemas import ConversationContext


@dataclass
class ConversationMemoryMetrics:
    context_hits: int = 0
    context_misses: int = 0
    clarification_resolutions: int = 0


memory_metrics = ConversationMemoryMetrics()


class ConversationMemoryService:
    """Almacenamiento en memoria del proceso (v1).

    Limitaciones:
    - No sobrevive reinicios del servidor.
    - No se comparte entre workers/instancias.
    - Sin TTL automático (sesiones permanecen hasta clear o eviction manual).
    """

    def __init__(self) -> None:
        self._store: dict[str, ConversationContext] = {}

    def get_context(self, session_id: str) -> ConversationContext | None:
        return self._store.get(session_id)

    def save_context(self, session_id: str, context: ConversationContext) -> None:
        context.session_id = session_id
        context.updated_at = datetime.now(timezone.utc)
        context.turn_count += 1
        self._store[session_id] = context

    def clear_context(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def get_or_create(self, session_id: str) -> ConversationContext:
        existing = self.get_context(session_id)
        if existing is not None:
            return existing
        now = datetime.now(timezone.utc)
        context = ConversationContext(
            session_id=session_id,
            created_at=now,
            updated_at=now,
        )
        self._store[session_id] = context
        return context

    def record_hit(self, *, clarification: bool = False) -> None:
        memory_metrics.context_hits += 1
        if clarification:
            memory_metrics.clarification_resolutions += 1

    def record_miss(self) -> None:
        memory_metrics.context_misses += 1

    @staticmethod
    def snapshot_metrics() -> dict[str, int]:
        return {
            "context_hits": memory_metrics.context_hits,
            "context_misses": memory_metrics.context_misses,
            "clarification_resolutions": memory_metrics.clarification_resolutions,
        }
