from unittest.mock import MagicMock

from app.api.routes.hybrid_chat import hybrid_chat
from app.conversation_ux.constants import GATEWAY_DECISION_CONVERSATION
from app.conversation_ux.gateway import ConversationIntelligenceGateway
from app.conversation_ux.presenter import ConversationPresenter
from app.conversation_ux.response_generator import ConversationResponseGenerator
from app.enterprise_knowledge_service.schemas import CapabilitiesPayload
from app.reasoning_engine.engine import EnterpriseReasoningEngine
from app.reasoning_engine.fallback import rule_based_decision
from app.reasoning_engine.governed_executor import GovernedRouteExecutor
from app.reasoning_engine.governor import ReasoningGovernor
from app.enterprise_personality.engine import EnterprisePersonalityEngine
from app.guided_fallback.engine import GuidedFallbackEngine
from app.schemas.hybrid_chat import HybridChatRequest, HybridChatResult
from tests.support.hybrid_chat_test_deps import disabled_executive_layers_kwargs


def _presenter() -> ConversationPresenter:
    return ConversationPresenter(
        knowledge_service=MagicMock(
            get_capabilities=MagicMock(
                return_value=CapabilitiesPayload(
                    answer="",
                    capabilities=["Clientes"],
                    examples=["¿Cuántos clientes existen?"],
                )
            ),
            get_faq=MagicMock(return_value=None),
        ),
        dataset_summary_provider=lambda: {"clientes": 10},
    )


def _governance_deps(presenter: ConversationPresenter) -> tuple[ReasoningGovernor, GovernedRouteExecutor]:
    institutional = MagicMock()
    institutional.execute.return_value = None
    institutional.resolve_system_capabilities.return_value = HybridChatResult(
        handled_by="product_identity",
        success=True,
        answer="Capacidades del sistema.",
    )
    executor = GovernedRouteExecutor(
        conversation_presenter=presenter,
        institutional_knowledge=institutional,
        guided_fallback_engine=GuidedFallbackEngine(),
    )
    return ReasoningGovernor(), executor


def test_hybrid_chat_skips_runtime_for_conversational_greeting() -> None:
    presenter = _presenter()
    gateway = ConversationIntelligenceGateway(presenter)
    runtime = MagicMock()
    generator = ConversationResponseGenerator(MagicMock(), enabled=False)

    reasoning_engine = EnterpriseReasoningEngine(MagicMock(), enabled=True)
    reasoning_engine.analyze = MagicMock(return_value=rule_based_decision("Hola"))
    governor, executor = _governance_deps(presenter)

    result = hybrid_chat(
        HybridChatRequest(message="Hola"),
        enterprise_runtime=runtime,
        conversation_gateway=gateway,
        conversation_presenter=presenter,
        conversation_response_generator=generator,
        enterprise_reasoning_engine=reasoning_engine,
        reasoning_governor=governor,
        governed_route_executor=executor,
        enterprise_personality_engine=EnterprisePersonalityEngine(),
        **disabled_executive_layers_kwargs(),
    )

    runtime.process_inquiry.assert_not_called()
    assert result.metadata["gateway_decision"] == GATEWAY_DECISION_CONVERSATION
    assert result.handled_by == "conversation_gateway"


def test_hybrid_chat_uses_runtime_for_business_query() -> None:
    gateway = ConversationIntelligenceGateway(_presenter())
    runtime = MagicMock()
    runtime.process_inquiry.return_value = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Actualmente existen 50 clientes registrados.",
        metadata={"query_type": "COUNT_CLIENTES"},
    )
    generator = ConversationResponseGenerator(MagicMock(), enabled=False)
    presenter = _presenter()

    reasoning_engine = EnterpriseReasoningEngine(MagicMock(), enabled=True)
    reasoning_engine.analyze = MagicMock(
        return_value=rule_based_decision("¿Cuántos clientes existen?")
    )
    governor, executor = _governance_deps(presenter)

    result = hybrid_chat(
        HybridChatRequest(message="¿Cuántos clientes existen?"),
        enterprise_runtime=runtime,
        conversation_gateway=gateway,
        conversation_presenter=presenter,
        conversation_response_generator=generator,
        enterprise_reasoning_engine=reasoning_engine,
        reasoning_governor=governor,
        governed_route_executor=executor,
        enterprise_personality_engine=EnterprisePersonalityEngine(),
        **disabled_executive_layers_kwargs(),
    )

    runtime.process_inquiry.assert_called_once()
    assert result.metadata["gateway_decision"] == "business"
    assert result.handled_by == "business_pipeline"
