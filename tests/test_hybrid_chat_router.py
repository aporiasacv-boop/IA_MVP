from unittest.mock import MagicMock

import pytest

from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.query_result import BusinessQueryResult
from app.response_engine.response_result import BusinessResponse
from app.schemas.chat import ChatResponse
from app.schemas.hybrid_chat import HybridChatResult
from app.schemas.response_mode import ResponseMode
from app.services.hybrid_chat_router import HybridChatRouter


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
    intent_builder: MagicMock,
    query_planner: MagicMock,
    query_executor: MagicMock,
    response_engine: MagicMock,
    legacy_handler: MagicMock,
) -> HybridChatRouter:
    return HybridChatRouter(
        intent_builder,
        query_planner,
        query_executor,
        response_engine,
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

    result = router.route("¿Cuántos clientes existen?")

    assert isinstance(result, HybridChatResult)
    assert result.handled_by == "business_pipeline"
    assert result.success is True
    assert "50 clientes" in result.answer
    assert result.metadata["query_type"] == "COUNT_CLIENTES"
    assert result.metadata["confidence"] == 1.0
    legacy_handler.assert_not_called()


def test_route_count_proveedores_uses_business_pipeline(
    router: HybridChatRouter,
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

    result = router.route("¿Cuántos proveedores existen?")

    assert result.handled_by == "business_pipeline"
    assert result.success is True
    assert "766 proveedores" in result.answer
    assert result.metadata["query_type"] == "COUNT_PROVEEDORES"
    legacy_handler.assert_not_called()


def test_route_top_clientes_uses_business_pipeline(
    router: HybridChatRouter,
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

    result = router.route("Muéstrame los principales clientes")

    assert result.handled_by == "business_pipeline"
    assert result.metadata["query_type"] == "TOP_CLIENTES"
    legacy_handler.assert_not_called()


def test_route_dataset_info_uses_business_pipeline(
    router: HybridChatRouter,
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

    result = router.route("¿Qué tipos de datos tienes?")

    assert result.handled_by == "business_pipeline"
    assert result.metadata["query_type"] == "DATASET_INFO"
    legacy_handler.assert_not_called()


def test_route_generic_question_uses_legacy_chat(
    router: HybridChatRouter,
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

    result = router.route("¿Qué es un proveedor?")

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

    result = router.route("Explícame qué observas en estos datos.")

    assert result.handled_by == "legacy_chat"
    assert result.success is True
    query_executor.execute.assert_not_called()
    legacy_handler.assert_called_once_with("Explícame qué observas en estos datos.")


def test_route_capability_discovery_que_puedes_hacer(
    router: HybridChatRouter,
    query_planner: MagicMock,
    query_executor: MagicMock,
    response_engine: MagicMock,
    legacy_handler: MagicMock,
) -> None:
    _configure_business_query(query_planner, BusinessQueryType.SYSTEM_CAPABILITIES)

    result = router.route("¿Qué puedes hacer?")

    assert result.handled_by == "capability_discovery"
    assert result.success is True
    assert result.answer.startswith("Puedo ayudarte con información sobre:")
    assert result.metadata["capabilities_count"] == 5
    assert result.metadata["example_questions_count"] == 3
    assert result.suggestions is None
    query_executor.execute.assert_not_called()
    response_engine.generate.assert_not_called()
    legacy_handler.assert_not_called()


def test_route_max_transaccion_without_cliente_uses_slot_clarification(
    router: HybridChatRouter,
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

    result = router.route("¿Cuál fue la transacción más alta?")

    assert result.handled_by == "slot_clarification"
    assert result.success is True
    assert "cliente" in result.answer.lower()
    assert result.metadata["pending_query_type"] == "MAX_TRANSACCION_CLIENTE"
    assert result.metadata["missing_slots"] == ["cliente_codigo"]
    assert result.metadata["session_token"]
    query_executor.execute.assert_not_called()
    response_engine.generate.assert_not_called()
    legacy_handler.assert_not_called()
