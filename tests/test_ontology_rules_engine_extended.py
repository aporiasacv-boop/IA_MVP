from decimal import Decimal

import pytest

from app.business_ontology.constants import CONCEPT_BEHAVIOR, CONCEPT_IDENTITY, CONCEPT_NATURE, CONCEPT_ROLE
from app.business_ontology.health import OntologyHealthError, validate_ontology_health
from app.business_ontology.rules_engine import OntologyEntityContext, evaluate_rule, generate_ontology_suggestions


def _ctx(**overrides) -> OntologyEntityContext:
    base = dict(
        canonical_id=1,
        canonical_name="ACME",
        primary_rfc=None,
        normalized_name="ACME",
        alias_count=1,
        total_movements=50,
        total_amount=Decimal("5000"),
        debit_amount=Decimal("3000"),
        credit_amount=Decimal("2000"),
        debit_credit_ratio=Decimal("1.5"),
        related_accounts_count=2,
        related_counterparties_count=1,
        active_months=4,
        dimensions_used=["cuenta_proveedor"],
        top_accounts=[{"code": "50101001", "name": "GASTOS ADMIN", "movements": 30, "amount": 3000}],
        top_counterparties=[],
        currencies=["MXN"],
    )
    base.update(overrides)
    return OntologyEntityContext(**base)


def test_identity_gl_account_only() -> None:
    result = evaluate_rule(
        _ctx(dimensions_used=["account_display_value"], total_movements=10),
        "identity_gl_account",
        {"requires_only_dimension": "account_display_value"},
        Decimal("0.92"),
    )
    assert result is not None


def test_role_vendor_only() -> None:
    result = evaluate_rule(
        _ctx(dimensions_used=["cuenta_proveedor"]),
        "role_vendor",
        {"requires_only_dimension": "cuenta_proveedor"},
        Decimal("0.92"),
    )
    assert result is not None


def test_role_bank_keyword() -> None:
    result = evaluate_rule(
        _ctx(top_accounts=[{"code": "10201001", "name": "BANCO BBVA", "movements": 40, "amount": 4000}]),
        "role_bank",
        {"account_keywords": ["BANCO", "CAJA"]},
        Decimal("0.88"),
    )
    assert result is not None
    assert "BANCO" in result.evidence.get("account_keyword_hits", [])


def test_nature_expense_prefix() -> None:
    result = evaluate_rule(
        _ctx(top_accounts=[{"code": "50101001", "name": "GASTOS", "movements": 90, "amount": 9000}]),
        "nature_expense",
        {"account_prefix": "5", "min_share": 0.5},
        Decimal("0.90"),
    )
    assert result is not None


def test_behavior_collection() -> None:
    result = evaluate_rule(
        _ctx(
            dimensions_used=["cuenta_cliente"],
            debit_amount=Decimal("2000"),
            credit_amount=Decimal("5000"),
        ),
        "behavior_collection",
        {"requires_dimension": "cuenta_cliente", "credit_exceeds_debit": True},
        Decimal("0.85"),
    )
    assert result is not None


def test_behavior_transfer_no_counterparties() -> None:
    result = evaluate_rule(
        _ctx(related_counterparties_count=0, total_movements=5),
        "behavior_transfer",
        {"max_counterparties": 0, "min_movements": 1},
        Decimal("0.82"),
    )
    assert result is not None


def test_behavior_mixed_balanced() -> None:
    result = evaluate_rule(
        _ctx(
            dimensions_used=["cuenta_cliente", "cuenta_proveedor"],
            debit_amount=Decimal("5000"),
            credit_amount=Decimal("4000"),
            debit_credit_ratio=Decimal("1.25"),
        ),
        "behavior_mixed",
        {"requires_all_dimensions": ["cuenta_cliente", "cuenta_proveedor"], "balanced_debit_credit": True},
        Decimal("0.75"),
    )
    assert result is not None


def test_behavior_admin_active_months() -> None:
    result = evaluate_rule(
        _ctx(active_months=6, top_accounts=[{"code": "50101001", "name": "ADMIN", "movements": 20, "amount": 2000}]),
        "behavior_admin",
        {"account_prefix": "5", "min_active_months": 3},
        Decimal("0.80"),
    )
    assert result is not None


def test_credit_ratio_min_rule() -> None:
    result = evaluate_rule(
        _ctx(debit_credit_ratio=Decimal("0.5")),
        "credit_dom",
        {"credit_ratio_min": 1.5},
        Decimal("0.85"),
    )
    assert result is not None


def test_requires_any_dimension_fails() -> None:
    result = evaluate_rule(
        _ctx(dimensions_used=["account_display_value"]),
        "commercial",
        {"requires_any_dimension": ["cuenta_cliente"]},
        Decimal("0.90"),
    )
    assert result is None


def test_excludes_commercial() -> None:
    result = evaluate_rule(
        _ctx(dimensions_used=["account_display_value"]),
        "gl_only",
        {"requires_dimension": "account_display_value", "excludes_commercial": True},
        Decimal("0.90"),
    )
    assert result is not None


def test_score_below_minimum_rejected() -> None:
    result = evaluate_rule(_ctx(), "low", {}, Decimal("0.40"))
    assert result is None


def test_health_incompatible_natures() -> None:
    with pytest.raises(OntologyHealthError, match="incompatibles"):
        validate_ontology_health(
            {
                "entities_without_suggestions": [],
                "contradictory_rules": [],
                "incompatible_natures": [{"canonical_id": 1}],
                "invalid_scores": [],
                "incomplete_relations": [],
            }
        )


def test_health_incomplete_relations() -> None:
    with pytest.raises(OntologyHealthError, match="incompletas"):
        validate_ontology_health(
            {
                "entities_without_suggestions": [],
                "contradictory_rules": [],
                "incompatible_natures": [],
                "invalid_scores": [],
                "incomplete_relations": [{"assignment_id": 1}],
            }
        )


def test_generate_full_rule_set() -> None:
    from app.business_ontology.taxonomy import build_rule_seeds

    rules = [
        (s.rule_code, s.concept_category, s.target_type_code, s.conditions_json, s.score_weight)
        for s in build_rule_seeds()
    ]
    results = generate_ontology_suggestions(_ctx(dimensions_used=["cuenta_proveedor"]), rules)
    assert len(results) >= 3
    categories = {r.concept_category for r in results}
    assert CONCEPT_ROLE in categories
