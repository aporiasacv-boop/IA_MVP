import pytest

from app.capabilities.conversation_context_capability import ConversationContextCapability
from app.conversation_memory.context_resolver import ContextResolver
from app.conversation_memory.schemas import ConversationContext
from app.conversation_memory.service import ConversationMemoryService, memory_metrics
from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.services.semantic_intent_builder import SemanticIntentBuilder
from app.slot_clarification.engine import SlotClarificationEngine


@pytest.fixture(autouse=True)
def reset_memory_metrics() -> None:
    memory_metrics.context_hits = 0
    memory_metrics.context_misses = 0
    memory_metrics.clarification_resolutions = 0


@pytest.fixture
def capability() -> ConversationContextCapability:
    return ConversationContextCapability(
        conversation_memory_service=ConversationMemoryService(),
        context_resolver=ContextResolver(),
    )


def test_prepare_session_creates_context(capability: ConversationContextCapability) -> None:
    session_id, context = capability.prepare_session("hola", None)

    assert session_id
    assert context.session_id == session_id


def test_prepare_session_clears_pending_on_new_question(
    capability: ConversationContextCapability,
) -> None:
    session_id = "sess-new-q"
    _, context = capability.prepare_session("primera", session_id)
    context.pending_clarification = {
        "pending_query_type": "MAX_TRANSACCION_CLIENTE",
        "missing_slots": ["cliente_codigo"],
        "session_token": "tok",
        "pending_filters": {},
    }
    capability.save_context(session_id, context)

    _, refreshed = capability.prepare_session("¿Cuántos clientes existen?", session_id)

    assert refreshed.pending_clarification is None


def test_resolve_pending_clarification(capability: ConversationContextCapability) -> None:
    context = ConversationContext(
        session_id="s1",
        last_query_type="MAX_TRANSACCION_CLIENTE",
        pending_clarification={
            "pending_query_type": "MAX_TRANSACCION_CLIENTE",
            "missing_slots": ["cliente_codigo"],
            "session_token": "tok-1",
            "pending_filters": {},
        },
    )

    resolution = capability.resolve("C001", context)

    assert resolution is not None
    assert resolution.resolution_type == "clarification"
    assert resolution.query.filters["cliente_codigo"] == "C001"


def test_record_memory_hit_increments_metrics(
    capability: ConversationContextCapability,
) -> None:
    context = ConversationContext(session_id="s1")
    resolution = capability.resolve(
        "C001",
        ConversationContext(
            session_id="s1",
            pending_clarification={
                "pending_query_type": "MAX_TRANSACCION_CLIENTE",
                "missing_slots": ["cliente_codigo"],
                "session_token": "tok",
                "pending_filters": {},
            },
        ),
    )
    assert resolution is not None

    capability.record_memory_hit(resolution)

    assert memory_metrics.context_hits == 1
    assert memory_metrics.clarification_resolutions == 1


def test_record_memory_miss_when_turns_exist(
    capability: ConversationContextCapability,
) -> None:
    context = ConversationContext(session_id="s1", turn_count=1)

    capability.record_memory_miss_if_applicable(context)

    assert memory_metrics.context_misses == 1


def test_finalize_memory_resolution_persists_context(
    capability: ConversationContextCapability,
) -> None:
    session_id = "finalize-session"
    _, context = capability.prepare_session("inicio", session_id)
    resolution = capability.resolve(
        "¿Y proveedores?",
        ConversationContext(
            session_id=session_id,
            last_query_type="COUNT_CLIENTES",
            last_operation=BusinessOperation.COUNT.value,
            last_target_entity=BusinessEntity.CLIENTE.value,
        ),
    )
    assert resolution is not None

    metadata = capability.finalize_memory_resolution(
        session_id,
        context,
        resolution.query,
        resolution,
    )

    assert metadata["context_hit"] is True
    assert metadata["resolution_type"] == resolution.resolution_type
    stored = capability._conversation_memory_service.get_context(session_id)
    assert stored is not None
    assert stored.last_query_type == "COUNT_PROVEEDORES"
    assert stored.pending_clarification is None


def test_persist_slot_clarification_sets_pending_state(
    capability: ConversationContextCapability,
) -> None:
    context = ConversationContext(session_id="slot-session")
    intent = SemanticIntentBuilder().build("¿Cuál fue la transacción más alta?")
    query = BusinessQuery(query_type=BusinessQueryType.MAX_TRANSACCION_CLIENTE)
    clarification = SlotClarificationEngine().resolve(intent, query)
    assert clarification is not None

    capability.persist_slot_clarification(context, intent, query, clarification)

    assert context.pending_clarification is not None
    assert context.pending_clarification["missing_slots"] == ["cliente_codigo"]
