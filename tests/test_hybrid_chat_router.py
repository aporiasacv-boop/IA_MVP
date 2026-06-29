from unittest.mock import MagicMock

import pytest

from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.capabilities.business_understanding_capability import BusinessUnderstandingCapability
from app.capabilities.business_resolution_capability import BusinessResolutionCapability
from app.capabilities.conversational_enrichment_capability import ConversationalEnrichmentCapability
from app.capabilities.executive_reasoning_capability import ExecutiveReasoningCapability
from app.capabilities.guided_fallback_capability import GuidedFallbackCapability
from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.query_result import BusinessQueryResult
from app.response_engine.response_result import BusinessResponse
from app.schemas.chat import ChatResponse
from app.schemas.hybrid_chat import HybridChatResult
from app.schemas.response_mode import ResponseMode
from app.services.hybrid_chat_router import HybridChatRouter
from app.slot_clarification.engine import SlotClarificationEngine


@pytest.fixture
def business_understanding(
    intent_builder: MagicMock,
    query_planner: MagicMock,
) -> BusinessUnderstandingCapability:
    return BusinessUnderstandingCapability(intent_builder, query_planner)


@pytest.fixture
def business_resolution(
    query_executor: MagicMock,
    response_engine: MagicMock,
) -> BusinessResolutionCapability:
    return BusinessResolutionCapability(query_executor, response_engine)


@pytest.fixture
def routing_pipeline(
    router: HybridChatRouter,
    conversation_context,
    business_understanding: BusinessUnderstandingCapability,
    business_resolution: BusinessResolutionCapability,
) -> BusinessPipelineCapability:
    return BusinessPipelineCapability(
        router,
        ConversationalEnrichmentCapability(),
        conversation_context,
        business_understanding,
        business_resolution,
        InstitutionalKnowledgeCapability(),
        ExecutiveReasoningCapability(),
        GuidedFallbackCapability(),
        slot_clarification_engine=SlotClarificationEngine(),
    )


@pytest.fixture
def legacy_handler() -> MagicMock:
    return MagicMock(
        return_value=ChatResponse(
            intent="UNKNOWN",
            answer="Respuesta legacy de prueba.",
            data=None,
            response_mode=ResponseMode.GENERATIVE,
        )
    )


@pytest.fixture
def intent_builder() -> MagicMock:
    builder = MagicMock()
    builder.build.return_value = MagicMock(confidence=0.95)
    return builder


@pytest.fixture
def query_planner() -> MagicMock:
    return MagicMock()


@pytest.fixture
def query_executor() -> MagicMock:
    return MagicMock()


@pytest.fixture
def response_engine() -> MagicMock:
    engine = MagicMock()
    engine.generate.return_value = BusinessResponse(
        success=True,
        answer="Respuesta empresarial de prueba.",
        query_type="COUNT_CLIENTES",
    )
    return engine


@pytest.fixture
def router(
    legacy_handler: MagicMock,
) -> HybridChatRouter:
    return HybridChatRouter(
        legacy_handler,
    )


def _configure_business_query(
    query_planner: MagicMock,
    query_type: BusinessQueryType,
    confidence: float = 0.95,
) -> None:
    query_planner.plan.return_value = BusinessQuery(query_type=query_type)


def test_route_count_clientes_uses_business_pipeline(
    router: HybridChatRouter,
    routing_pipeline: BusinessPipelineCapability,
    intent_builder: MagicMock,
    query_planner: MagicMock,
    query_executor: MagicMock,
    response_engine: MagicMock,
    legacy_handler: MagicMock,
) -> None:
    intent_builder.build.return_value = MagicMock(confidence=1.0)
    _configure_business_query(query_planner, BusinessQueryType.COUNT_CLIENTES)
    query_executor.execute.return_value = BusinessQueryResult(
        query_type="COUNT_CLIENTES",
        success=True,
        data={"total": 50},
    )
    response_engine.generate.return_value = BusinessResponse(
        success=True,
        answer="Actualmente existen 50 clientes registrados.",
        query_type="COUNT_CLIENTES",
    )

    result = routing_pipeline.execute("¿Cuántos clientes existen?")

    assert isinstance(result, HybridChatResult)
    assert result.handled_by == "business_pipeline"
    assert result.success is True
    assert "50 clientes" in result.answer
    assert result.metadata["query_type"] == "COUNT_CLIENTES"
    assert result.metadata["confidence"] == 1.0
    legacy_handler.assert_not_called()


def test_route_count_proveedores_uses_business_pipeline(
    router: HybridChatRouter,
    routing_pipeline: BusinessPipelineCapability,
    query_planner: MagicMock,
    query_executor: MagicMock,
    response_engine: MagicMock,
    legacy_handler: MagicMock,
) -> None:
    _configure_business_query(query_planner, BusinessQueryType.COUNT_PROVEEDORES)
    query_executor.execute.return_value = BusinessQueryResult(
        query_type="COUNT_PROVEEDORES",
        success=True,
        data={"total": 766},
    )
    response_engine.generate.return_value = BusinessResponse(
        success=True,
        answer="Actualmente existen 766 proveedores registrados.",
        query_type="COUNT_PROVEEDORES",
    )

    result = routing_pipeline.execute("¿Cuántos proveedores existen?")

    assert result.handled_by == "business_pipeline"
    assert result.success is True
    assert "766 proveedores" in result.answer
    assert result.metadata["query_type"] == "COUNT_PROVEEDORES"
    legacy_handler.assert_not_called()


def test_route_top_clientes_uses_business_pipeline(
    router: HybridChatRouter,
    routing_pipeline: BusinessPipelineCapability,
    query_planner: MagicMock,
    query_executor: MagicMock,
    response_engine: MagicMock,
    legacy_handler: MagicMock,
) -> None:
    _configure_business_query(query_planner, BusinessQueryType.TOP_CLIENTES)
    query_executor.execute.return_value = BusinessQueryResult(
        query_type="TOP_CLIENTES",
        success=True,
        data={"items": []},
    )
    response_engine.generate.return_value = BusinessResponse(
        success=True,
        answer="Los principales clientes identificados son:",
        query_type="TOP_CLIENTES",
    )

    result = routing_pipeline.execute("Muéstrame los principales clientes")

    assert result.handled_by == "business_pipeline"
    assert result.metadata["query_type"] == "TOP_CLIENTES"
    legacy_handler.assert_not_called()


def test_route_dataset_info_uses_business_pipeline(
    router: HybridChatRouter,
    routing_pipeline: BusinessPipelineCapability,
    query_planner: MagicMock,
    query_executor: MagicMock,
    response_engine: MagicMock,
    legacy_handler: MagicMock,
) -> None:
    _configure_business_query(query_planner, BusinessQueryType.DATASET_INFO)
    query_executor.execute.return_value = BusinessQueryResult(
        query_type="DATASET_INFO",
        success=True,
        data={},
    )
    response_engine.generate.return_value = BusinessResponse(
        success=True,
        answer="Actualmente analizo datos empresariales.",
        query_type="DATASET_INFO",
    )

    result = routing_pipeline.execute("¿Qué tipos de datos tienes?")

    assert result.handled_by == "business_pipeline"
    assert result.metadata["query_type"] == "DATASET_INFO"
    legacy_handler.assert_not_called()


def test_route_generic_question_uses_legacy_chat(
    router: HybridChatRouter,
    routing_pipeline: BusinessPipelineCapability,
    query_planner: MagicMock,
    query_executor: MagicMock,
    response_engine: MagicMock,
    legacy_handler: MagicMock,
) -> None:
    _configure_business_query(query_planner, BusinessQueryType.UNSUPPORTED)
    legacy_handler.return_value = ChatResponse(
        intent="UNKNOWN",
        answer="Un proveedor es una entidad que suministra bienes o servicios.",
        data=None,
        response_mode=ResponseMode.GENERATIVE,
        intent_confidence=0.4,
    )

    result = routing_pipeline.execute("¿Qué es un proveedor?")

    assert result.handled_by == "legacy_chat"
    assert result.success is True
    assert result.answer
    assert result.metadata["intent"] == "UNKNOWN"
    assert result.metadata["response_mode"] == "GENERATIVE"
    query_executor.execute.assert_not_called()
    response_engine.generate.assert_not_called()
    legacy_handler.assert_called_once_with("¿Qué es un proveedor?")


def test_route_conversational_question_uses_legacy_chat(
    router: HybridChatRouter,
    routing_pipeline: BusinessPipelineCapability,
    query_planner: MagicMock,
    query_executor: MagicMock,
    response_engine: MagicMock,
    legacy_handler: MagicMock,
) -> None:
    _configure_business_query(query_planner, BusinessQueryType.UNSUPPORTED)
    legacy_handler.return_value = ChatResponse(
        intent="UNKNOWN",
        answer="Observo variaciones en volumen y concentracion por cliente.",
        data=None,
        response_mode=ResponseMode.GENERATIVE,
        intent_confidence=0.3,
    )

    result = routing_pipeline.execute("Explícame qué observas en estos datos.")

    assert result.handled_by == "legacy_chat"
    assert result.success is True
    query_executor.execute.assert_not_called()
    legacy_handler.assert_called_once_with("Explícame qué observas en estos datos.")


def test_route_system_capabilities_redirects_to_business_knowledge(
    router: HybridChatRouter,
    routing_pipeline: BusinessPipelineCapability,
    query_planner: MagicMock,
    query_executor: MagicMock,
    response_engine: MagicMock,
    legacy_handler: MagicMock,
) -> None:
    _configure_business_query(query_planner, BusinessQueryType.SYSTEM_CAPABILITIES)

    result = routing_pipeline.execute("¿Qué puedo preguntarte?")

    assert result.handled_by == "business_knowledge"
    assert result.success is True
    assert "Clientes" in result.answer or "clientes" in result.answer.lower()
    query_executor.execute.assert_not_called()
    response_engine.generate.assert_not_called()
    legacy_handler.assert_not_called()


def test_route_max_transaccion_without_cliente_uses_slot_clarification(
    router: HybridChatRouter,
    routing_pipeline: BusinessPipelineCapability,
    intent_builder: MagicMock,
    query_planner: MagicMock,
    query_executor: MagicMock,
    response_engine: MagicMock,
    legacy_handler: MagicMock,
) -> None:
    intent_builder.build.return_value = MagicMock(confidence=0.92)
    query_planner.plan.return_value = BusinessQuery(
        query_type=BusinessQueryType.MAX_TRANSACCION_CLIENTE,
    )

    result = routing_pipeline.execute("¿Cuál fue la transacción más alta?")

    assert result.handled_by == "slot_clarification"
    assert result.success is True
    assert "cliente" in result.answer.lower()
    assert result.metadata["pending_query_type"] == "MAX_TRANSACCION_CLIENTE"
    assert result.metadata["missing_slots"] == ["cliente_codigo"]
    assert result.metadata["session_token"]
    query_executor.execute.assert_not_called()
    response_engine.generate.assert_not_called()
    legacy_handler.assert_not_called()
