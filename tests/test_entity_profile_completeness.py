from datetime import date
from decimal import Decimal

from app.business_entity_profile.completeness import compute_debit_credit_ratio, compute_profile_completeness


def test_debit_credit_ratio() -> None:
    assert compute_debit_credit_ratio(Decimal("200"), Decimal("100")) == Decimal("2.0")
    assert compute_debit_credit_ratio(Decimal("100"), Decimal("0")) is None


def test_completeness_zero_movements() -> None:
    assert compute_profile_completeness(
        total_movements=0,
        total_amount=Decimal("0"),
        average_amount=Decimal("0"),
        first_seen=None,
        last_seen=None,
        active_months=0,
        active_days=0,
        monthly_distribution={},
        debit_amount=Decimal("0"),
        credit_amount=Decimal("0"),
        related_accounts_count=0,
        related_counterparties_count=0,
        currencies=[],
        journals={},
        dimensions_used=[],
    ) == Decimal("0.0000")


def test_completeness_full_profile() -> None:
    monthly = {"2024-01": {"movements": 5, "amount": 100}}
    score = compute_profile_completeness(
        total_movements=10,
        total_amount=Decimal("1000"),
        average_amount=Decimal("100"),
        first_seen=date(2024, 1, 1),
        last_seen=date(2024, 6, 1),
        active_months=1,
        active_days=5,
        monthly_distribution=monthly,
        debit_amount=Decimal("600"),
        credit_amount=Decimal("400"),
        related_accounts_count=2,
        related_counterparties_count=1,
        currencies=["MXN"],
        journals={"distinct_count": 2, "top": []},
        dimensions_used=["cuenta_cliente"],
    )
    assert score > Decimal("0.5")
