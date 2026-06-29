import pytest

from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.capabilities.business_resolution_capability import BusinessResolutionCapability
from app.capabilities.conversational_enrichment_capability import ConversationalEnrichmentCapability
from app.capabilities.executive_reasoning_capability import ExecutiveReasoningCapability
from app.capabilities.guided_fallback_capability import GuidedFallbackCapability
from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.capabilities.conversation_context_capability import ConversationContextCapability
from app.conversation_memory.context_resolver import ContextResolver, is_new_question
from app.conversation_memory.schemas import ConversationContext
from app.conversation_memory.service import ConversationMemoryService, memory_metrics
from app.conversation_memory.slot_value_parser import parse_slot_value
from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation
from app.query_engine.business_query import BusinessQuery
from app.capabilities.business_understanding_capability import BusinessUnderstandingCapability
from app.query_engine.query_planner import BusinessQueryPlanner
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.query_result import BusinessQueryResult
from app.response_engine.deterministic_response_engine import DeterministicResponseEngine
from app.response_engine.response_result import BusinessResponse
from app.schemas.chat import ChatResponse
from app.schemas.response_mode import ResponseMode
from app.services.hybrid_chat_router import HybridChatRouter
from app.services.semantic_intent_builder import SemanticIntentBuilder
from app.slot_clarification.engine import SlotClarificationEngine
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def reset_memory_metrics() -> None:
    memory_metrics.context_hits = 0
    memory_metrics.context_misses = 0
    memory_metrics.clarification_resolutions = 0


@pytest.fixture
def memory_service() -> ConversationMemoryService:
    return ConversationMemoryService()


@pytest.fixture
def context_resolver() -> ContextResolver:
    return ContextResolver()


def test_parse_cliente_codigo() -> None:
    assert parse_slot_value("C001", "cliente_codigo") == "C001"


def test_parse_mes_name() -> None:
    assert parse_slot_value("julio", "mes") == 7


def test_resolve_pending_clarification_cliente(
    context_resolver: ContextResolver,
) -> None:
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

    resolution = context_resolver.resolve("C001", context)

    assert resolution is not None
    assert resolution.resolution_type == "clarification"
    assert resolution.query.query_type == BusinessQueryType.MAX_TRANSACCION_CLIENTE
    assert resolution.query.filters["cliente_codigo"] == "C001"


def test_resolve_pending_clarification_mes(context_resolver: ContextResolver) -> None:
    context = ConversationContext(
        session_id="s1",
        last_query_type="MAX_PROVEEDOR_MES",
        pending_clarification={
            "pending_query_type": "MAX_PROVEEDOR_MES",
            "missing_slots": ["mes"],
            "session_token": "tok-2",
            "pending_filters": {},
        },
    )

    resolution = context_resolver.resolve("junio", context)

    assert resolution is not None
    assert resolution.query.query_type == BusinessQueryType.MAX_PROVEEDOR_MES
    assert resolution.query.filters["mes"] == 6


def test_resolve_follow_up_proveedores(context_resolver: ContextResolver) -> None:
    context = ConversationContext(
        session_id="s1",
        last_query_type="COUNT_CLIENTES",
        last_operation=BusinessOperation.COUNT.value,
        last_target_entity=BusinessEntity.CLIENTE.value,
    )

    resolution = context_resolver.resolve("¿Y proveedores?", context)

    assert resolution is not None
    assert resolution.resolution_type == "follow_up"
    assert resolution.query.query_type == BusinessQueryType.COUNT_PROVEEDORES


def test_resolve_follow_up_julio(context_resolver: ContextResolver) -> None:
    context = ConversationContext(
        session_id="s1",
        last_query_type="MAX_PROVEEDOR_MES",
        last_operation=BusinessOperation.MAX.value,
        last_target_entity=BusinessEntity.PROVEEDOR.value,
        last_filters={"mes": 6},
    )

    resolution = context_resolver.resolve("¿Y en julio?", context)

    assert resolution is not None
    assert resolution.query.query_type == BusinessQueryType.MAX_PROVEEDOR_MES
    assert resolution.query.filters["mes"] == 7


def test_resolve_follow_up_agosto(context_resolver: ContextResolver) -> None:
    context = ConversationContext(
        session_id="s1",
        last_query_type="MAX_PROVEEDOR_MES",
        last_operation=BusinessOperation.MAX.value,
        last_target_entity=BusinessEntity.PROVEEDOR.value,
        last_filters={"mes": 7},
    )

    resolution = context_resolver.resolve("¿Y agosto?", context)

    assert resolution is not None
    assert resolution.query.filters["mes"] == 8


def test_new_question_ignores_pending_clarification(
    context_resolver: ContextResolver,
) -> None:
    context = ConversationContext(
        session_id="s1",
        pending_clarification={
            "pending_query_type": "MAX_TRANSACCION_CLIENTE",
            "missing_slots": ["cliente_codigo"],
            "session_token": "tok-3",
            "pending_filters": {},
        },
    )

    assert is_new_question("¿Cuántos clientes existen?") is True
    assert context_resolver.resolve("¿Cuántos clientes existen?", context) is None


def test_memory_service_roundtrip(memory_service: ConversationMemoryService) -> None:
    context = ConversationContext(session_id="sess-1", last_query_type="COUNT_CLIENTES")
    memory_service.save_context("sess-1", context)

    loaded = memory_service.get_context("sess-1")

    assert loaded is not None
    assert loaded.last_query_type == "COUNT_CLIENTES"
    assert loaded.turn_count == 1


@pytest.fixture
def shared_conversation_context() -> ConversationContextCapability:
    return ConversationContextCapability(
        conversation_memory_service=ConversationMemoryService(),
        context_resolver=ContextResolver(),
    )


@pytest.fixture
def memory_query_executor() -> MagicMock:
    executor = MagicMock()
    executor.execute.return_value = BusinessQueryResult(
        query_type="COUNT_PROVEEDORES",
        success=True,
        data={"total": 10},
    )
    return executor


@pytest.fixture
def memory_router(shared_conversation_context: ConversationContextCapability) -> HybridChatRouter:
    legacy_handler = MagicMock(
        return_value=ChatResponse(
            intent="UNKNOWN",
            answer="legacy",
            data=None,
            response_mode=ResponseMode.GENERATIVE,
        )
    )
    return HybridChatRouter(
        legacy_handler,
        conversation_context=shared_conversation_context,
    )


@pytest.fixture
def shared_business_resolution(
    memory_query_executor: MagicMock,
) -> BusinessResolutionCapability:
    return BusinessResolutionCapability(
        memory_query_executor,
        DeterministicResponseEngine(),
    )


@pytest.fixture
def shared_business_understanding() -> BusinessUnderstandingCapability:
    return BusinessUnderstandingCapability(
        SemanticIntentBuilder(),
        BusinessQueryPlanner(),
    )


@pytest.fixture
def memory_pipeline(
    memory_router: HybridChatRouter,
    shared_conversation_context: ConversationContextCapability,
    shared_business_understanding: BusinessUnderstandingCapability,
    shared_business_resolution: BusinessResolutionCapability,
) -> BusinessPipelineCapability:
    return BusinessPipelineCapability(
        memory_router,
        ConversationalEnrichmentCapability(),
        shared_conversation_context,
        shared_business_understanding,
        shared_business_resolution,
        InstitutionalKnowledgeCapability(),
        ExecutiveReasoningCapability(),
        GuidedFallbackCapability(),
        slot_clarification_engine=SlotClarificationEngine(),
    )


def test_router_clarification_then_cliente_resolution(
    memory_pipeline: BusinessPipelineCapability,
    memory_query_executor: MagicMock,
) -> None:
    session_id = "clarify-session"
    first = memory_pipeline.execute(
        "¿Cuál fue la transacción más alta?",
        session_id=session_id,
    )

    assert first.handled_by == "slot_clarification"
    assert first.metadata["missing_slots"] == ["cliente_codigo"]

    second = memory_pipeline.execute("C001", session_id=session_id)

    assert second.handled_by == "conversation_memory"
    assert second.metadata["clarification_resolved"] is True
    assert second.metadata["query_type"] == "MAX_TRANSACCION_CLIENTE"
    memory_query_executor.execute.assert_called_once()


def test_router_count_then_follow_up_proveedores(
    memory_pipeline: BusinessPipelineCapability,
    memory_query_executor: MagicMock,
) -> None:
    session_id = "followup-session"
    memory_query_executor.execute.return_value = BusinessQueryResult(
        query_type="COUNT_CLIENTES",
        success=True,
        data={"total": 50},
    )

    first = memory_pipeline.execute("¿Cuántos clientes existen?", session_id=session_id)
    assert first.handled_by == "business_pipeline"

    memory_query_executor.execute.return_value = BusinessQueryResult(
        query_type="COUNT_PROVEEDORES",
        success=True,
        data={"total": 20},
    )
    second = memory_pipeline.execute("¿Y proveedores?", session_id=session_id)

    assert second.handled_by == "conversation_memory"
    assert second.metadata["resolution_type"] == "follow_up"
    assert "20 proveedores" in second.answer
