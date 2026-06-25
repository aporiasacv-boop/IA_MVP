import pytest

from app.enterprise_reasoning.health import ReasoningHealthError, validate_reasoning_health
from app.enterprise_reasoning.rule_evaluator import EkoEvaluationContext, evaluate_condition, evaluate_rule
from app.enterprise_reasoning.schemas import ReasoningRuleDefinition
from tests.test_enterprise_reasoning_builder import _sample_eko


def test_evaluate_all_of() -> None:
    ctx = EkoEvaluationContext.from_eko(_sample_eko())
    ok, _ = evaluate_condition(
        ctx,
        {"all_of": [{"eko_roles_include": "CLIENTE"}, {"eko_fact_min": {"field": "total_movements", "threshold": 100}}]},
    )
    assert ok is True


def test_evaluate_not() -> None:
    ctx = EkoEvaluationContext.from_eko(_sample_eko())
    ok, _ = evaluate_condition(ctx, {"not": {"eko_alert_present": "missing_profile"}})
    assert ok is True


def test_evaluate_rule_returns_evidence() -> None:
    ctx = EkoEvaluationContext.from_eko(_sample_eko())
    rule = ReasoningRuleDefinition(
        rule_code="r1",
        conclusion_type="finding",
        key="k1",
        value="v",
        conditions={"eko_signal_present": "debit_dominant"},
        pack_id="p",
    )
    ok, evidence, value = evaluate_rule(ctx, rule)
    assert ok is True
    assert evidence["rule_code"] == "r1"


def test_evaluate_any_of() -> None:
    ctx = EkoEvaluationContext.from_eko(_sample_eko())
    ok, _ = evaluate_condition(ctx, {"any_of": [{"eko_roles_include": "CLIENTE"}, {"eko_roles_include": "OTRO"}]})
    assert ok is True


def test_evaluate_fact_conditions() -> None:
    ctx = EkoEvaluationContext.from_eko(_sample_eko())
    ok, _ = evaluate_condition(ctx, {"eko_fact_max": {"field": "related_counterparties_count", "threshold": 10}})
    assert ok is True
    ok2, _ = evaluate_condition(ctx, {"eko_fact_equals": {"field": "total_movements", "value": 150}})
    assert ok2 is True


def test_evaluate_quality_conditions() -> None:
    ctx = EkoEvaluationContext.from_eko(_sample_eko())
    ok, _ = evaluate_condition(ctx, {"eko_quality_has_profile": True})
    assert ok is True


def test_resolve_value_from_eko_fact() -> None:
    from app.enterprise_reasoning.rule_evaluator import resolve_conclusion_value

    ctx = EkoEvaluationContext.from_eko(_sample_eko())
    rule = ReasoningRuleDefinition(
        rule_code="r",
        conclusion_type="finding",
        key="k",
        value_from="eko_fact",
        value_ref="total_movements",
        pack_id="p",
    )
    value = resolve_conclusion_value(ctx, rule, {})
    assert value == 150


def test_evaluate_unknown_condition() -> None:
    ctx = EkoEvaluationContext.from_eko(_sample_eko())
    ok, evidence = evaluate_condition(ctx, {"unknown_op": True})
    assert ok is False
    assert evidence.get("error") == "unknown_condition"


def test_evaluate_signal_and_nature() -> None:
    ctx = EkoEvaluationContext.from_eko(_sample_eko())
    ok, _ = evaluate_condition(ctx, {"eko_signal_present": "debit_dominant"})
    assert ok is True
    ok2, _ = evaluate_condition(ctx, {"eko_roles_count_min": 1})
    assert ok2 is True


def test_health_missing_evidence() -> None:
    with pytest.raises(ReasoningHealthError, match="confidence"):
        validate_reasoning_health({"invalid_confidence": [{"reasoning_id": 1}]})

    with pytest.raises(ReasoningHealthError, match="evidencia"):
        validate_reasoning_health({"missing_evidence": [{"reasoning_id": 1}]})
