from unittest.mock import MagicMock

import pytest

from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.capabilities.business_resolution_capability import BusinessResolutionCapability
from app.capabilities.business_understanding_capability import BusinessUnderstandingCapability
from app.capabilities.conversational_enrichment_capability import ConversationalEnrichmentCapability
from app.capabilities.executive_reasoning_capability import ExecutiveReasoningCapability
from app.capabilities.guided_fallback_capability import GuidedFallbackCapability
from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_planner import BusinessQueryPlanner
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.query_result import BusinessQueryResult
from app.response_engine.response_result import BusinessResponse
from app.schemas.chat import ChatResponse
from app.schemas.hybrid_chat import HybridChatResult
from app.schemas.response_mode import ResponseMode
from app.services.hybrid_chat_router import HybridChatRouter
from app.services.semantic_intent_builder import SemanticIntentBuilder
from app.slot_clarification.engine import SlotClarificationEngine


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
    understanding = BusinessUnderstandingCapability(builder, planner).understand(question)

    assert understanding.result.query.query_type == expected_type
    assert understanding.result.query.query_type != BusinessQueryType.UNSUPPORTED


@pytest.fixture
def routing_pipeline(
    conversation_context,
) -> BusinessPipelineCapability:
    intent_builder = MagicMock()
    intent_builder.build.return_value = MagicMock(confidence=1.0)

    query_planner = MagicMock()
    query_planner.plan.return_value = BusinessQuery(
        query_type=BusinessQueryType.SYSTEM_CAPABILITIES,
    )

    query_executor = MagicMock()
    response_engine = MagicMock()
    legacy_handler = MagicMock()

    router = HybridChatRouter(legacy_handler)
    business_understanding = BusinessUnderstandingCapability(intent_builder, query_planner)
    business_resolution = BusinessResolutionCapability(query_executor, response_engine)
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


def test_pipeline_resolves_system_capabilities_via_institutional_knowledge(
    routing_pipeline: BusinessPipelineCapability,
) -> None:
    result = routing_pipeline.execute("¿Qué puedo preguntarte?")

    assert isinstance(result, HybridChatResult)
    assert result.handled_by == "business_knowledge"
    assert result.success is True
    routing_pipeline._business_resolution._query_executor.execute.assert_not_called()
    routing_pipeline._business_resolution._response_engine.generate.assert_not_called()


@pytest.mark.parametrize(
    ("query_type", "answer_snippet"),
    [
        (BusinessQueryType.DATA_COVERAGE, "abarcan desde"),
        (BusinessQueryType.DATASET_INFO, "Actualmente analizo"),
    ],
)
def test_hybrid_router_uses_business_pipeline_for_system_queries(
    conversation_context,
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

    router = HybridChatRouter(legacy_handler)
    pipeline = BusinessPipelineCapability(
        router,
        ConversationalEnrichmentCapability(),
        conversation_context,
        BusinessUnderstandingCapability(intent_builder, query_planner),
        BusinessResolutionCapability(query_executor, response_engine),
        InstitutionalKnowledgeCapability(),
        ExecutiveReasoningCapability(),
        GuidedFallbackCapability(),
        slot_clarification_engine=SlotClarificationEngine(),
    )

    result = pipeline.execute("pregunta de prueba")

    assert isinstance(result, HybridChatResult)
    assert result.handled_by == "business_pipeline"
    assert result.metadata["query_type"] == query_type.value
    assert answer_snippet in result.answer
    legacy_handler.assert_not_called()
