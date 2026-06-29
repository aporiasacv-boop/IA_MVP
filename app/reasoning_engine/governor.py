from dataclasses import dataclass

from app.core.settings import settings
from app.reasoning_engine.constants import (
    ROUTE_BUSINESS_PIPELINE,
    ROUTE_CLARIFICATION,
    ROUTE_CONVERSATION,
    ROUTE_EXECUTIVE_ANALYSIS,
    ROUTE_INSTITUTIONAL_KNOWLEDGE,
    ROUTE_LEGACY,
    VALID_ROUTES,
)
from app.reasoning_engine.schemas import ReasoningDecision

GOVERNANCE_RULE_GOVERNED = "governed"
GOVERNANCE_RULE_OBSERVATION = "observation"
GOVERNANCE_RULE_FALLBACK = "fallback"


@dataclass(frozen=True)
class GovernanceOutcome:
    governed: bool
    route: str | None
    rule: str
    reason: str
    confidence: float
    time_ms: float
    pipeline_skipped: bool = False

    def to_metadata(self) -> dict:
        return {
            "reasoning_governed": self.governed,
            "governance_rule": self.rule,
            "governance_reason": self.reason,
            "governance_confidence": round(self.confidence, 4),
            "governance_time_ms": round(self.time_ms, 2),
            "pipeline_skipped": self.pipeline_skipped,
        }


class ReasoningGovernor:
    """Aplica política de gobernanza sobre la decisión del Reasoning Engine."""

    _GOVERNED_ROUTES = frozenset({
        ROUTE_CONVERSATION,
        ROUTE_INSTITUTIONAL_KNOWLEDGE,
        ROUTE_CLARIFICATION,
    })

    def evaluate(self, decision: ReasoningDecision | None) -> GovernanceOutcome:
        import time

        started = time.perf_counter()
        elapsed_ms = lambda: (time.perf_counter() - started) * 1000

        if not settings.REASONING_GOVERNANCE:
            return GovernanceOutcome(
                governed=False,
                route=None,
                rule=GOVERNANCE_RULE_OBSERVATION,
                reason="governance_disabled",
                confidence=decision.confidence if decision else 0.0,
                time_ms=elapsed_ms(),
            )

        if decision is None:
            return GovernanceOutcome(
                governed=False,
                route=None,
                rule=GOVERNANCE_RULE_FALLBACK,
                reason="missing_reasoning_decision",
                confidence=0.0,
                time_ms=elapsed_ms(),
            )

        if decision.recommended_route not in VALID_ROUTES:
            return GovernanceOutcome(
                governed=False,
                route=decision.recommended_route,
                rule=GOVERNANCE_RULE_FALLBACK,
                reason="unknown_route",
                confidence=decision.confidence,
                time_ms=elapsed_ms(),
            )

        if decision.confidence < settings.REASONING_MIN_CONFIDENCE:
            return GovernanceOutcome(
                governed=False,
                route=decision.recommended_route,
                rule=GOVERNANCE_RULE_FALLBACK,
                reason="insufficient_confidence",
                confidence=decision.confidence,
                time_ms=elapsed_ms(),
            )

        if not self._is_route_governance_enabled(decision.recommended_route):
            return GovernanceOutcome(
                governed=False,
                route=decision.recommended_route,
                rule=GOVERNANCE_RULE_OBSERVATION,
                reason="route_in_observation_mode",
                confidence=decision.confidence,
                time_ms=elapsed_ms(),
            )

        if decision.recommended_route not in self._GOVERNED_ROUTES:
            return GovernanceOutcome(
                governed=False,
                route=decision.recommended_route,
                rule=GOVERNANCE_RULE_OBSERVATION,
                reason="route_not_governed",
                confidence=decision.confidence,
                time_ms=elapsed_ms(),
            )

        return GovernanceOutcome(
            governed=True,
            route=decision.recommended_route,
            rule=GOVERNANCE_RULE_GOVERNED,
            reason=f"governed_{decision.recommended_route}",
            confidence=decision.confidence,
            time_ms=elapsed_ms(),
            pipeline_skipped=True,
        )

    @staticmethod
    def _is_route_governance_enabled(route: str) -> bool:
        mapping = {
            ROUTE_CONVERSATION: settings.REASONING_ROUTE_CONVERSATION,
            ROUTE_INSTITUTIONAL_KNOWLEDGE: settings.REASONING_ROUTE_INSTITUTIONAL,
            ROUTE_CLARIFICATION: settings.REASONING_ROUTE_CLARIFICATION,
            ROUTE_BUSINESS_PIPELINE: settings.REASONING_ROUTE_BUSINESS,
            ROUTE_EXECUTIVE_ANALYSIS: settings.REASONING_ROUTE_EXECUTIVE,
            ROUTE_LEGACY: settings.REASONING_ROUTE_LEGACY,
        }
        return mapping.get(route, False)
