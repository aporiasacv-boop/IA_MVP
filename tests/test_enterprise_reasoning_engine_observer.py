from unittest.mock import MagicMock

import pytest

from app.conversation_ux.constants import GATEWAY_DECISION_BUSINESS, GATEWAY_DECISION_CONVERSATION
from app.conversation_ux.gateway import GatewayRouteOutcome
from app.reasoning_engine.constants import (
    ROUTE_BUSINESS_PIPELINE,
    ROUTE_CONVERSATION,
    ROUTE_INSTITUTIONAL_KNOWLEDGE,
)
from app.reasoning_engine.engine import EnterpriseReasoningEngine
from app.reasoning_engine.metrics import get_metrics, reset_metrics
from app.reasoning_engine.route_resolver import resolve_actual_route
from app.reasoning_engine.schemas import ReasoningDecision
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture(autouse=True)
def _reset_metrics() -> None:
    reset_metrics()


def test_observe_records_match_for_business_query() -> None:
    engine = EnterpriseReasoningEngine(MagicMock(), enabled=True)
    decision = ReasoningDecision(
        intent="business_query",
        confidence=0.94,
        recommended_route=ROUTE_BUSINESS_PIPELINE,
        explanation="Consulta empresarial.",
    )
    result = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Actualmente existen 50 clientes registrados.",
        metadata={"query_type": "COUNT_CLIENTES"},
    )
    gateway = GatewayRouteOutcome(
        decision=GATEWAY_DECISION_BUSINESS,
        reason="business_query",
        time_ms=1.0,
    )

    observed = engine.observe(decision, result, gateway)

    assert observed.metadata["reasoning_route"] == ROUTE_BUSINESS_PIPELINE
    assert observed.metadata["reasoning_actual_route"] == ROUTE_BUSINESS_PIPELINE
    assert observed.metadata["reasoning_route_match"] is True
    assert get_metrics().match_rate == 1.0


def test_observe_records_mismatch_for_capabilities() -> None:
    engine = EnterpriseReasoningEngine(MagicMock(), enabled=True)
    decision = ReasoningDecision(
        intent="capabilities",
        confidence=0.94,
        recommended_route=ROUTE_INSTITUTIONAL_KNOWLEDGE,
        explanation="Capacidades institucionales.",
    )
    result = HybridChatResult(
        handled_by="conversation_gateway",
        success=True,
        answer="Puedo ayudarte con clientes y proveedores.",
        metadata={"gateway_decision": GATEWAY_DECISION_CONVERSATION},
    )
    gateway = GatewayRouteOutcome(
        decision=GATEWAY_DECISION_CONVERSATION,
        reason="capabilities",
        time_ms=1.0,
        result=result,
    )

    observed = engine.observe(decision, result, gateway)

    assert observed.metadata["reasoning_actual_route"] == ROUTE_CONVERSATION
    assert observed.metadata["reasoning_route_match"] is False
    assert get_metrics().match_rate == 0.0


def test_resolve_actual_route_for_conversation_gateway() -> None:
    result = HybridChatResult(
        handled_by="conversation_gateway",
        success=True,
        answer="Hola",
        metadata={},
    )
    gateway = GatewayRouteOutcome(
        decision=GATEWAY_DECISION_CONVERSATION,
        reason="greeting",
        time_ms=0.5,
        result=result,
    )
    assert resolve_actual_route(result, gateway) == ROUTE_CONVERSATION
