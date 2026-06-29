import time

from app.ai_orchestration.providers.base import BaseLLMProvider
from app.conversation_ux.gateway import GatewayRouteOutcome
from app.core.settings import settings
from app.reasoning_engine.fallback import rule_based_decision
from app.reasoning_engine.metrics import record_observation
from app.reasoning_engine.parser import parse_reasoning_response
from app.reasoning_engine.prompt import build_reasoning_prompt
from app.reasoning_engine.route_resolver import resolve_actual_route
from app.reasoning_engine.schemas import ReasoningDecision, ReasoningObservation
from app.schemas.hybrid_chat import HybridChatResult


class EnterpriseReasoningEngine:
    """Clasifica la intención global del usuario sin ejecutar flujos de negocio."""

    def __init__(
        self,
        llm_provider: BaseLLMProvider | None = None,
        *,
        enabled: bool | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._enabled = (
            settings.ENTERPRISE_REASONING_ENGINE_ENABLED if enabled is None else enabled
        )

    def analyze(self, message: str) -> ReasoningDecision | None:
        if not self._enabled:
            return None

        started = time.perf_counter()
        try:
            decision = self._analyze_with_llm(message)
        except Exception:
            decision = rule_based_decision(message)
            decision = decision.model_copy(
                update={
                    "reasoning_time_ms": (time.perf_counter() - started) * 1000,
                    "source": "rules_fallback",
                }
            )
            return decision

        decision = decision.model_copy(
            update={"reasoning_time_ms": (time.perf_counter() - started) * 1000}
        )
        return decision

    def observe(
        self,
        decision: ReasoningDecision | None,
        result: HybridChatResult,
        gateway_outcome: GatewayRouteOutcome,
    ) -> HybridChatResult:
        if decision is None:
            return result

        actual_route = resolve_actual_route(result, gateway_outcome)
        observation = ReasoningObservation(
            recommended_route=decision.recommended_route,
            actual_route=actual_route,
            route_match=decision.recommended_route == actual_route,
        )
        record_observation(route_match=observation.route_match)

        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={
                **result.metadata,
                **decision.to_metadata(),
                **observation.to_metadata(),
            },
        )

    def _analyze_with_llm(self, message: str) -> ReasoningDecision:
        provider = self._resolve_provider()
        prompt = build_reasoning_prompt(message)
        llm_result = provider.generate_response(prompt)
        decision = parse_reasoning_response(llm_result.text)
        return decision.model_copy(
            update={
                "provider": llm_result.provider or provider.provider_name(),
                "model": llm_result.model or provider.model_name,
                "source": "llm",
            }
        )

    def _resolve_provider(self) -> BaseLLMProvider:
        if self._llm_provider is None:
            from app.ai_orchestration.providers.factory import create_llm_provider_with_fallback

            self._llm_provider = create_llm_provider_with_fallback()
        return self._llm_provider
