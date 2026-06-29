import uuid

from app.conversation_memory.context_resolver import (
    ContextResolution,
    ContextResolver,
    is_new_question,
)
from app.conversation_memory.schemas import ConversationContext
from app.conversation_memory.service import ConversationMemoryService
from app.query_engine.business_query import BusinessQuery
from app.schemas.semantic_intent import BusinessSemanticIntent
from app.slot_clarification.schemas import SlotClarificationResult


class ConversationContextCapability:
    """Construye, recupera y resuelve el contexto conversacional para el pipeline."""

    def __init__(
        self,
        conversation_memory_service: ConversationMemoryService | None = None,
        context_resolver: ContextResolver | None = None,
    ) -> None:
        self._conversation_memory_service = (
            conversation_memory_service or ConversationMemoryService()
        )
        self._context_resolver = context_resolver or ContextResolver()

    def prepare_session(
        self,
        message: str,
        session_id: str | None,
    ) -> tuple[str, ConversationContext]:
        resolved_session_id = session_id or uuid.uuid4().hex
        context = self._conversation_memory_service.get_or_create(resolved_session_id)

        if context.pending_clarification and is_new_question(message):
            context.pending_clarification = None
            self._conversation_memory_service.save_context(resolved_session_id, context)

        return resolved_session_id, context

    def resolve(
        self,
        message: str,
        context: ConversationContext,
    ) -> ContextResolution | None:
        return self._context_resolver.resolve(message, context)

    def record_memory_hit(self, resolution: ContextResolution) -> None:
        self._conversation_memory_service.record_hit(
            clarification=resolution.resolution_type == "clarification",
        )

    def record_memory_miss_if_applicable(self, context: ConversationContext) -> None:
        if context.turn_count > 0 or context.pending_clarification:
            self._conversation_memory_service.record_miss()

    def save_context(self, session_id: str, context: ConversationContext) -> None:
        self._conversation_memory_service.save_context(session_id, context)

    def persist_slot_clarification(
        self,
        context: ConversationContext,
        intent: BusinessSemanticIntent,
        query: BusinessQuery,
        clarification: SlotClarificationResult,
    ) -> None:
        context.last_query_type = clarification.pending_query_type
        context.last_operation = (
            intent.operation.value if intent.operation is not None else None
        )
        context.last_target_entity = (
            intent.target_entity.value if intent.target_entity is not None else None
        )
        context.last_filters = dict(query.filters)
        context.pending_clarification = {
            "pending_query_type": clarification.pending_query_type,
            "missing_slots": clarification.missing_slots,
            "session_token": clarification.session_token,
            "pending_filters": clarification.metadata.get("pending_filters", {}),
        }

    def persist_successful_query(
        self,
        context: ConversationContext,
        intent: BusinessSemanticIntent,
        query: BusinessQuery,
    ) -> None:
        context.last_query_type = query.query_type.value
        context.last_operation = (
            intent.operation.value if intent.operation is not None else None
        )
        context.last_target_entity = (
            intent.target_entity.value if intent.target_entity is not None else None
        )
        context.last_filters = dict(query.filters)

    def finalize_memory_resolution(
        self,
        session_id: str,
        context: ConversationContext,
        query: BusinessQuery,
        resolution: ContextResolution,
    ) -> dict:
        context.last_query_type = query.query_type.value
        context.last_filters = dict(query.filters)
        context.pending_clarification = None
        self.save_context(session_id, context)
        return self.build_memory_metadata(
            context_hit=True,
            resolution_type=resolution.resolution_type,
            inherited_from=resolution.inherited_from,
            clarification_resolved=resolution.resolution_type == "clarification",
        )

    @staticmethod
    def build_memory_metadata(
        *,
        context_hit: bool,
        resolution_type: str,
        inherited_from: str,
        clarification_resolved: bool,
    ) -> dict:
        snapshot = ConversationMemoryService.snapshot_metrics()
        return {
            "context_hit": context_hit,
            "resolution_type": resolution_type,
            "inherited_from": inherited_from,
            "clarification_resolved": clarification_resolved,
            "context_hits": snapshot["context_hits"],
            "context_misses": snapshot["context_misses"],
            "clarification_resolutions": snapshot["clarification_resolutions"],
        }
