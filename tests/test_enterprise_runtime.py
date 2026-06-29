from unittest.mock import ANY, MagicMock

from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.capabilities.executive_reasoning_capability import ExecutiveReasoningCapability
from app.capabilities.guided_fallback_capability import GuidedFallbackCapability
from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.conversation_memory.schemas import ConversationContext
from app.capability_executor.executor import CapabilityExecutor
from app.capability_registry.registry import CapabilityRegistry
from app.enterprise_runtime.runtime import EnterpriseRuntime
from app.execution_plan.plan import ExecutionPlan
from app.schemas.hybrid_chat import HybridChatResult
from app.services.hybrid_chat_router import HybridRouteOutcome


def _passthrough_enrichment() -> MagicMock:
    enrichment = MagicMock()
    enrichment.enrich.side_effect = lambda result, context=None: result
    return enrichment


def _runtime(hybrid_router: MagicMock) -> EnterpriseRuntime:
    conversation_context = MagicMock()
    conversation_context.prepare_session.return_value = ("abc", ConversationContext(session_id="abc"))
    conversation_context.resolve.return_value = None
    registry = CapabilityRegistry(
        business_pipeline=BusinessPipelineCapability(
            hybrid_router,
            _passthrough_enrichment(),
            conversation_context,
            MagicMock(),
            MagicMock(),
            InstitutionalKnowledgeCapability(),
            ExecutiveReasoningCapability(),
            GuidedFallbackCapability(),
        ),
    )
    return EnterpriseRuntime(
        ExecutionPlan.default_inquiry(),
        CapabilityExecutor(registry),
    )


def test_process_inquiry_returns_product_identity_without_router():
    hybrid_router = MagicMock()
    runtime = _runtime(hybrid_router)

    result = runtime.process_inquiry("como te llamas")

    assert result.handled_by == "product_identity"
    assert result.success is True
    hybrid_router.route.assert_not_called()


def test_process_inquiry_delegates_to_hybrid_router_when_no_institutional_match():
    hybrid_router = MagicMock()
    expected = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Actualmente existen 50 clientes registrados.",
        metadata={"query_type": "COUNT_CLIENTES"},
    )
    hybrid_router.route.return_value = HybridRouteOutcome(result=expected)
    runtime = _runtime(hybrid_router)

    result = runtime.process_inquiry("cuantos clientes existen", session_id="abc123")

    hybrid_router.route.assert_called_once_with(
        "cuantos clientes existen",
        pipeline_state=ANY,
    )
    assert result is expected
