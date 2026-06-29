import pytest

from app.core import settings as settings_module
from app.reasoning_engine.constants import (
    ROUTE_BUSINESS_PIPELINE,
    ROUTE_CLARIFICATION,
    ROUTE_CONVERSATION,
    ROUTE_EXECUTIVE_ANALYSIS,
    ROUTE_INSTITUTIONAL_KNOWLEDGE,
)
from app.reasoning_engine.fallback import rule_based_decision
from app.reasoning_engine.governor import (
    GOVERNANCE_RULE_FALLBACK,
    GOVERNANCE_RULE_GOVERNED,
    GOVERNANCE_RULE_OBSERVATION,
    ReasoningGovernor,
)
from app.reasoning_engine.schemas import ReasoningDecision


@pytest.fixture
def governor() -> ReasoningGovernor:
    return ReasoningGovernor()


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


def test_governor_applies_conversation_route(governor: ReasoningGovernor) -> None:
    decision = rule_based_decision("Hola")
    outcome = governor.evaluate(decision)

    assert outcome.governed is True
    assert outcome.route == ROUTE_CONVERSATION
    assert outcome.rule == GOVERNANCE_RULE_GOVERNED
    assert outcome.pipeline_skipped is True


def test_governor_applies_institutional_route(governor: ReasoningGovernor) -> None:
    decision = rule_based_decision("¿Quién eres?")
    outcome = governor.evaluate(decision)

    assert outcome.governed is True
    assert outcome.route == ROUTE_INSTITUTIONAL_KNOWLEDGE
    assert outcome.pipeline_skipped is True


def test_governor_applies_clarification_route(governor: ReasoningGovernor) -> None:
    decision = rule_based_decision("No entiendo.")
    outcome = governor.evaluate(decision)

    assert outcome.governed is True
    assert outcome.route == ROUTE_CLARIFICATION
    assert outcome.pipeline_skipped is True


def test_governor_observes_business_pipeline(governor: ReasoningGovernor) -> None:
    decision = rule_based_decision("¿Cuántos clientes existen?")
    outcome = governor.evaluate(decision)

    assert outcome.governed is False
    assert outcome.route == ROUTE_BUSINESS_PIPELINE
    assert outcome.rule == GOVERNANCE_RULE_OBSERVATION
    assert outcome.reason == "route_in_observation_mode"
    assert outcome.pipeline_skipped is False


def test_governor_observes_executive_analysis(governor: ReasoningGovernor) -> None:
    decision = rule_based_decision("Resumen de junio.")
    outcome = governor.evaluate(decision)

    assert outcome.governed is False
    assert outcome.route == ROUTE_EXECUTIVE_ANALYSIS
    assert outcome.rule == GOVERNANCE_RULE_OBSERVATION


def test_governor_fallback_on_low_confidence(governor: ReasoningGovernor) -> None:
    decision = ReasoningDecision(
        intent="unknown",
        confidence=0.4,
        recommended_route=ROUTE_CONVERSATION,
        explanation="Baja confianza.",
        source="rules",
    )
    outcome = governor.evaluate(decision)

    assert outcome.governed is False
    assert outcome.rule == GOVERNANCE_RULE_FALLBACK
    assert outcome.reason == "insufficient_confidence"


def test_governor_fallback_on_missing_decision(governor: ReasoningGovernor) -> None:
    outcome = governor.evaluate(None)

    assert outcome.governed is False
    assert outcome.rule == GOVERNANCE_RULE_FALLBACK
    assert outcome.reason == "missing_reasoning_decision"


def test_governor_fallback_on_unknown_route(governor: ReasoningGovernor) -> None:
    decision = ReasoningDecision(
        intent="unknown",
        confidence=0.95,
        recommended_route="unknown_route",
        explanation="Ruta inválida.",
        source="rules",
    )
    outcome = governor.evaluate(decision)

    assert outcome.governed is False
    assert outcome.rule == GOVERNANCE_RULE_FALLBACK
    assert outcome.reason == "unknown_route"


def test_governor_disabled_returns_observation(
    governor: ReasoningGovernor,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings_module.settings, "REASONING_GOVERNANCE", False)
    decision = rule_based_decision("Hola")
    outcome = governor.evaluate(decision)

    assert outcome.governed is False
    assert outcome.rule == GOVERNANCE_RULE_OBSERVATION
    assert outcome.reason == "governance_disabled"


def test_governor_metadata_fields(governor: ReasoningGovernor) -> None:
    decision = rule_based_decision("Hola")
    outcome = governor.evaluate(decision)
    metadata = outcome.to_metadata()

    assert metadata["reasoning_governed"] is True
    assert metadata["governance_rule"] == GOVERNANCE_RULE_GOVERNED
    assert metadata["governance_reason"].startswith("governed_")
    assert metadata["governance_confidence"] >= 0.75
    assert metadata["pipeline_skipped"] is True
