from decimal import Decimal

from app.business_ontology.constants import CONCEPT_ROLE
from app.business_ontology.rules_engine import OntologyEntityContext, evaluate_rule, generate_ontology_suggestions


def _ctx(**overrides) -> OntologyEntityContext:
    base = dict(
        canonical_id=1,
        canonical_name="WALMART",
        primary_rfc="NWM9709244",
        normalized_name="WALMART",
        alias_count=1,
        total_movements=100,
        total_amount=Decimal("10000"),
        debit_amount=Decimal("6000"),
        credit_amount=Decimal("4000"),
        debit_credit_ratio=Decimal("1.5"),
        related_accounts_count=3,
        related_counterparties_count=2,
        active_months=6,
        dimensions_used=["cuenta_cliente"],
        top_accounts=[{"code": "40101001", "name": "VENTAS", "movements": 50, "amount": 5000}],
        top_counterparties=[],
        currencies=["MXN"],
    )
    base.update(overrides)
    return OntologyEntityContext(**base)


def test_role_client_only_dimension() -> None:
    suggestion = evaluate_rule(
        _ctx(dimensions_used=["cuenta_cliente"]),
        "role_client_dimension",
        {"requires_only_dimension": "cuenta_cliente"},
        Decimal("0.92"),
    )
    assert suggestion is not None
    assert float(suggestion.score) >= 0.55


def test_role_dual_commercial() -> None:
    suggestion = evaluate_rule(
        _ctx(dimensions_used=["cuenta_cliente", "cuenta_proveedor"]),
        "role_dual_commercial",
        {"requires_all_dimensions": ["cuenta_cliente", "cuenta_proveedor"]},
        Decimal("0.90"),
    )
    assert suggestion is not None


def test_nature_income_prefix() -> None:
    suggestion = evaluate_rule(
        _ctx(top_accounts=[{"code": "40101001", "name": "VENTAS", "movements": 80, "amount": 8000}]),
        "nature_income_prefix",
        {"account_prefix": "4", "min_share": 0.5},
        Decimal("0.90"),
    )
    assert suggestion is not None
    assert suggestion.evidence["prefix_share"] >= 0.5


def test_behavior_payment_requires_debit() -> None:
    suggestion = evaluate_rule(
        _ctx(dimensions_used=["cuenta_proveedor"], debit_amount=Decimal("8000"), credit_amount=Decimal("2000")),
        "behavior_payment",
        {"requires_dimension": "cuenta_proveedor", "debit_exceeds_credit": True},
        Decimal("0.85"),
    )
    assert suggestion is not None


def test_zero_movements_rejected_when_min_required() -> None:
    suggestion = evaluate_rule(
        _ctx(total_movements=0, debit_amount=Decimal("0"), credit_amount=Decimal("0")),
        "behavior_transfer",
        {"min_movements": 1, "max_counterparties": 0},
        Decimal("0.82"),
    )
    assert suggestion is None


def test_generate_multiple_suggestions() -> None:
    rules = [
        ("role_client_dimension", CONCEPT_ROLE, "CLIENTE", {"requires_only_dimension": "cuenta_cliente"}, Decimal("0.92")),
        ("role_vendor_dimension", CONCEPT_ROLE, "PROVEEDOR", {"requires_only_dimension": "cuenta_proveedor"}, Decimal("0.92")),
    ]
    results = generate_ontology_suggestions(_ctx(), rules)
    assert len(results) == 1
    assert results[0].type_code == "CLIENTE"
