from unittest.mock import MagicMock

import pytest

from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_planner import BusinessQueryPlanner
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.query_result import BusinessQueryResult
from app.response_engine.deterministic_response_engine import DeterministicResponseEngine
from app.response_engine.response_result import BusinessResponse
from app.schemas.chat import ChatResponse
from app.schemas.hybrid_chat import HybridChatResult
from app.schemas.response_mode import ResponseMode
from app.services.hybrid_chat_router import HybridChatRouter
from app.services.semantic_intent_builder import SemanticIntentBuilder


@pytest.fixture
def planner() -> BusinessQueryPlanner:
    return BusinessQueryPlanner()


@pytest.fixture
def builder() -> SemanticIntentBuilder:
    return SemanticIntentBuilder()


@pytest.mark.parametrize(
    ("question", "expected_type"),
    [
        ("¿Cuál es el periodo de los datos?", BusinessQueryType.DATA_COVERAGE),
        ("¿Qué fechas cubren los datos?", BusinessQueryType.DATA_COVERAGE),
        ("¿De qué fecha son tus datos?", BusinessQueryType.DATA_COVERAGE),
        ("¿Cuántos datos tienes?", BusinessQueryType.DATASET_INFO),
        ("¿Qué datos tienes?", BusinessQueryType.DATASET_INFO),
        ("¿Qué tipos de datos tienes?", BusinessQueryType.DATASET_INFO),
    ],
)
def test_system_capability_questions_do_not_plan_as_unsupported(
    builder: SemanticIntentBuilder,
    planner: BusinessQueryPlanner,
    question: str,
    expected_type: BusinessQueryType,
) -> None:
    intent = builder.build(question)
    result = planner.plan(intent)

    assert result.query_type == expected_type
    assert result.query_type != BusinessQueryType.UNSUPPORTED


def test_hybrid_router_redirects_system_capabilities_to_business_knowledge() -> None:
    intent_builder = MagicMock()
    intent_builder.build.return_value = MagicMock(confidence=1.0)

    query_planner = MagicMock()
    query_planner.plan.return_value = BusinessQuery(
        query_type=BusinessQueryType.SYSTEM_CAPABILITIES,
    )

    query_executor = MagicMock()
    response_engine = MagicMock()
    legacy_handler = MagicMock()

    router = HybridChatRouter(
        intent_builder,
        query_planner,
        query_executor,
        response_engine,
        legacy_handler,
    )

    result = router.route("¿Qué puedo preguntarte?")

    assert isinstance(result, HybridChatResult)
    assert result.handled_by == "business_knowledge"
    assert result.success is True
    query_executor.execute.assert_not_called()
    response_engine.generate.assert_not_called()
    legacy_handler.assert_not_called()


@pytest.mark.parametrize(
    ("query_type", "answer_snippet"),
    [
        (BusinessQueryType.DATA_COVERAGE, "abarcan desde"),
        (BusinessQueryType.DATASET_INFO, "Actualmente analizo"),
    ],
)
def test_hybrid_router_uses_business_pipeline_for_system_queries(
    query_type: BusinessQueryType,
    answer_snippet: str,
) -> None:
    intent_builder = MagicMock()
    intent_builder.build.return_value = MagicMock(confidence=1.0)

    query_planner = MagicMock()
    query_planner.plan.return_value = BusinessQuery(query_type=query_type)

    query_executor = MagicMock()
    query_executor.execute.return_value = BusinessQueryResult(
        query_type=query_type.value,
        success=True,
        data={},
    )

    response_engine = MagicMock()
    response_engine.generate.return_value = BusinessResponse(
        success=True,
        answer=f"Respuesta determinística: {answer_snippet}",
        query_type=query_type.value,
    )

    legacy_handler = MagicMock(
        return_value=ChatResponse(
            intent="UNKNOWN",
            answer="Respuesta legacy.",
            data=None,
            response_mode=ResponseMode.GENERATIVE,
        )
    )

    router = HybridChatRouter(
        intent_builder,
        query_planner,
        query_executor,
        response_engine,
        legacy_handler,
    )

    result = router.route("pregunta de prueba")

    assert isinstance(result, HybridChatResult)
    assert result.handled_by == "business_pipeline"
    assert result.metadata["query_type"] == query_type.value
    assert answer_snippet in result.answer
    legacy_handler.assert_not_called()
