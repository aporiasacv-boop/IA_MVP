from app.conversation_ux.constants import GATEWAY_DECISION_CONVERSATION
from app.conversation_ux.gateway import GatewayRouteOutcome
from app.reasoning_engine.constants import (
    ROUTE_BUSINESS_PIPELINE,
    ROUTE_CLARIFICATION,
    ROUTE_CONVERSATION,
    ROUTE_EXECUTIVE_ANALYSIS,
    ROUTE_INSTITUTIONAL_KNOWLEDGE,
    ROUTE_LEGACY,
)
from app.schemas.hybrid_chat import HybridChatResult

_EXECUTIVE_QUERY_TYPES = frozenset({
    "EXECUTIVE_SUMMARY",
    "BUSINESS_SUMMARY",
})


def resolve_actual_route(
    result: HybridChatResult,
    gateway_outcome: GatewayRouteOutcome,
) -> str:
    if result.metadata.get("reasoning_governed") is True:
        governed_route = result.metadata.get("governance_route")
        if isinstance(governed_route, str) and governed_route:
            return governed_route

    if gateway_outcome.decision == GATEWAY_DECISION_CONVERSATION:
        return ROUTE_CONVERSATION

    handled_by = result.handled_by
    if handled_by == "slot_clarification":
        return ROUTE_CLARIFICATION
    if handled_by == "executive_reasoning":
        return ROUTE_EXECUTIVE_ANALYSIS
    if handled_by in {"product_identity", "business_knowledge"}:
        return ROUTE_INSTITUTIONAL_KNOWLEDGE
    if handled_by == "legacy_chat":
        return ROUTE_LEGACY
    if handled_by == "guided_fallback":
        fallback_type = result.metadata.get("fallback_type")
        if fallback_type in {"LOW_CONFIDENCE", "UNSUPPORTED_CAPABILITY"}:
            return ROUTE_CLARIFICATION
        return ROUTE_CONVERSATION

    query_type = str(result.metadata.get("query_type", "")).upper()
    if query_type in _EXECUTIVE_QUERY_TYPES:
        return ROUTE_EXECUTIVE_ANALYSIS

    if handled_by in {"business_pipeline", "conversation_memory"}:
        return ROUTE_BUSINESS_PIPELINE

    return ROUTE_BUSINESS_PIPELINE
