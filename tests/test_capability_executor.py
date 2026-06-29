from unittest.mock import ANY, MagicMock

from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.capabilities.executive_reasoning_capability import ExecutiveReasoningCapability
from app.capabilities.guided_fallback_capability import GuidedFallbackCapability
from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.capability_executor.executor import CapabilityExecutor
from app.capability_registry.constants import BUSINESS_PIPELINE, INSTITUTIONAL_KNOWLEDGE
from app.capability_registry.registry import CapabilityRegistry
from app.conversation_memory.schemas import ConversationContext
from app.execution_plan.step import ExecutionStep
from app.schemas.hybrid_chat import HybridChatResult
from app.services.hybrid_chat_router import HybridRouteOutcome


def _passthrough_enrichment() -> MagicMock:
    enrichment = MagicMock()
    enrichment.enrich.side_effect = lambda result, context=None: result
    return enrichment


def _business_pipeline(router: MagicMock) -> BusinessPipelineCapability:
    conversation_context = MagicMock()
    conversation_context.prepare_session.return_value = ("abc", ConversationContext(session_id="abc"))
    conversation_context.resolve.return_value = None
    business_understanding = MagicMock()
    return BusinessPipelineCapability(
        router,
        _passthrough_enrichment(),
        conversation_context,
        business_understanding,
        MagicMock(),
        InstitutionalKnowledgeCapability(),
        ExecutiveReasoningCapability(),
        GuidedFallbackCapability(),
    )


def test_execute_institutional_step_returns_none_when_no_match():
    institutional = MagicMock()
    institutional.execute.return_value = None
    router = MagicMock()
    registry = CapabilityRegistry(
        institutional_knowledge=institutional,
        business_pipeline=_business_pipeline(router),
    )
    executor = CapabilityExecutor(registry)

    result = executor.execute(
        ExecutionStep(step_id=INSTITUTIONAL_KNOWLEDGE),
        "cuantos clientes existen",
    )

    assert result is None
    router.route.assert_not_called()


def test_execute_business_pipeline_step_delegates_to_router():
    institutional = MagicMock()
    institutional.execute.return_value = None
    router = MagicMock()
    expected = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="ok",
        metadata={},
    )
    router.route.return_value = HybridRouteOutcome(result=expected)
    registry = CapabilityRegistry(
        institutional_knowledge=institutional,
        business_pipeline=_business_pipeline(router),
    )
    executor = CapabilityExecutor(registry)

    result = executor.execute(
        ExecutionStep(step_id=BUSINESS_PIPELINE),
        "cuantos clientes existen",
        session_id="abc",
    )

    router.route.assert_called_once_with(
        "cuantos clientes existen",
        pipeline_state=ANY,
    )
    assert result is expected
