from unittest.mock import MagicMock

import pytest

from app.api.routes.hybrid_chat import hybrid_chat
from app.conversation_ux.constants import GATEWAY_DECISION_CONVERSATION
from app.conversation_ux.gateway import ConversationIntelligenceGateway
from app.conversation_ux.presenter import ConversationPresenter
from app.conversation_ux.response_generator import ConversationResponseGenerator
from app.core import settings as settings_module
from app.enterprise_knowledge_service.schemas import CapabilitiesPayload
from app.guided_fallback.engine import GuidedFallbackEngine
from app.reasoning_engine.engine import EnterpriseReasoningEngine
from app.reasoning_engine.fallback import rule_based_decision
from app.enterprise_personality.engine import EnterprisePersonalityEngine
from app.reasoning_engine.governed_executor import GovernedRouteExecutor
from app.reasoning_engine.governor import ReasoningGovernor
from app.reasoning_engine.metrics import get_governance_metrics, reset_metrics
from app.schemas.hybrid_chat import HybridChatRequest, HybridChatResult
from tests.support.hybrid_chat_test_deps import disabled_executive_layers_kwargs


@pytest.fixture(autouse=True)
def enable_governance(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings_module.settings, "REASONING_GOVERNANCE", True)
    monkeypatch.setattr(settings_module.settings, "REASONING_MIN_CONFIDENCE", 0.75)
    monkeypatch.setattr(settings_module.settings, "REASONING_ROUTE_CONVERSATION", True)
    monkeypatch.setattr(settings_module.settings, "REASONING_ROUTE_INSTITUTIONAL", True)
    monkeypatch.setattr(settings_module.settings, "REASONING_ROUTE_CLARIFICATION", True)
    monkeypatch.setattr(settings_module.settings, "REASONING_ROUTE_BUSINESS", False)
    monkeypatch.setattr(settings_module.settings, "REASONING_ROUTE_EXECUTIVE", False)
    monkeypatch.setattr(settings_module.settings, "REASONING_ROUTE_LEGACY", False)


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
        answer="Soy Olnatura Intelligence, tu asistente empresarial.",
        metadata={"source": "institutional_test"},
    )
    executor = GovernedRouteExecutor(
        conversation_presenter=presenter,
        institutional_knowledge=institutional,
        guided_fallback_engine=GuidedFallbackEngine(),
    )
    return ReasoningGovernor(), executor


def _hybrid_chat(
    message: str,
    *,
    runtime: MagicMock,
    presenter: ConversationPresenter | None = None,
    reasoning_engine: EnterpriseReasoningEngine | None = None,
) -> HybridChatResult:
    presenter = presenter or _presenter()
    gateway = ConversationIntelligenceGateway(presenter)
    generator = ConversationResponseGenerator(MagicMock(), enabled=False)
    governor, executor = _governance_deps(presenter)

    if reasoning_engine is None:
        reasoning_engine = EnterpriseReasoningEngine(MagicMock(), enabled=True)
        reasoning_engine.analyze = MagicMock(return_value=rule_based_decision(message))

    return hybrid_chat(
        HybridChatRequest(message=message),
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


def test_governed_greeting_skips_runtime_and_pipeline() -> None:
    reset_metrics()
    runtime = MagicMock()
    result = _hybrid_chat("Hola", runtime=runtime)

    runtime.process_inquiry.assert_not_called()
    assert result.metadata["reasoning_governed"] is True
    assert result.metadata["governance_rule"] == "governed"
    assert result.metadata["pipeline_skipped"] is True
    assert result.metadata.get("personality_applied") is True
    assert result.metadata["gateway_decision"] == GATEWAY_DECISION_CONVERSATION


def test_governed_capabilities_skips_runtime() -> None:
    runtime = MagicMock()
    result = _hybrid_chat("¿Qué puedes hacer?", runtime=runtime)

    runtime.process_inquiry.assert_not_called()
    assert result.metadata["reasoning_governed"] is True
    assert result.metadata["governance_route"] == "institutional_knowledge"
    assert result.metadata["pipeline_skipped"] is True


def test_governed_clarification_skips_runtime() -> None:
    runtime = MagicMock()
    result = _hybrid_chat("No entiendo.", runtime=runtime)

    runtime.process_inquiry.assert_not_called()
    assert result.metadata["reasoning_governed"] is True
    assert result.metadata["governance_route"] == "clarification"
    assert result.metadata["pipeline_skipped"] is True


def test_business_query_uses_runtime_when_not_governed() -> None:
    runtime = MagicMock()
    runtime.process_inquiry.return_value = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Actualmente existen 50 clientes registrados.",
        metadata={"query_type": "COUNT_CLIENTES"},
    )
    result = _hybrid_chat("¿Cuántos clientes existen?", runtime=runtime)

    runtime.process_inquiry.assert_called_once()
    assert result.metadata["reasoning_governed"] is False
    assert result.metadata["governance_rule"] == "observation"
    assert result.metadata.get("pipeline_skipped") is not True
    assert result.metadata.get("personality_applied") is not True
    assert result.handled_by == "business_pipeline"


def test_executive_query_uses_runtime_in_observation_mode() -> None:
    runtime = MagicMock()
    runtime.process_inquiry.return_value = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Resumen ejecutivo de junio.",
        metadata={"query_type": "EXECUTIVE_SUMMARY"},
    )
    result = _hybrid_chat("Resumen de junio.", runtime=runtime)

    runtime.process_inquiry.assert_called_once()
    assert result.metadata["reasoning_governed"] is False
    assert result.metadata["governance_rule"] == "observation"


def test_governance_metrics_record_pipeline_skipped() -> None:
    reset_metrics()
    runtime = MagicMock()
    runtime.process_inquiry.return_value = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="50 clientes.",
        metadata={"query_type": "COUNT_CLIENTES"},
    )
    _hybrid_chat("Hola", runtime=runtime)
    _hybrid_chat("¿Cuántos clientes existen?", runtime=runtime)

    metrics = get_governance_metrics()
    assert metrics.total_evaluations == 2
    assert metrics.governed_applied == 1
    assert metrics.pipeline_skipped == 1
