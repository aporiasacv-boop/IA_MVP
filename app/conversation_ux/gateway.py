import time
from dataclasses import dataclass

from app.conversation_ux.classifier import ConversationCategory, classify_message, is_conversational
from app.conversation_ux.presenter import ConversationPresenter
from app.schemas.hybrid_chat import HybridChatResult

from app.conversation_ux.constants import (
    GATEWAY_DECISION_BUSINESS,
    GATEWAY_DECISION_CONVERSATION,
    HANDLED_BY_CONVERSATION_GATEWAY,
)


@dataclass(frozen=True)
class GatewayRouteOutcome:
    decision: str
    reason: str
    time_ms: float
    result: HybridChatResult | None = None

    def metadata(self) -> dict:
        return {
            "gateway_decision": self.decision,
            "gateway_time_ms": round(self.time_ms, 2),
            "gateway_reason": self.reason,
        }


class ConversationIntelligenceGateway:
    """Punto de entrada conversacional: clasifica antes del Runtime empresarial."""

    def __init__(self, presenter: ConversationPresenter) -> None:
        self._presenter = presenter

    def route(self, message: str, session_id: str | None = None) -> GatewayRouteOutcome:
        started = time.perf_counter()
        category = classify_message(message)
        elapsed_ms = (time.perf_counter() - started) * 1000

        if is_conversational(category):
            result = self._presenter.compose(message, category, session_id=session_id)
            return GatewayRouteOutcome(
                decision=GATEWAY_DECISION_CONVERSATION,
                reason=category.value,
                time_ms=elapsed_ms,
                result=result,
            )

        return GatewayRouteOutcome(
            decision=GATEWAY_DECISION_BUSINESS,
            reason="business_query",
            time_ms=elapsed_ms,
            result=None,
        )

    @staticmethod
    def apply_metadata(result: HybridChatResult, outcome: GatewayRouteOutcome) -> HybridChatResult:
        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={**result.metadata, **outcome.metadata()},
        )
