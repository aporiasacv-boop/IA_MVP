from datetime import date
from decimal import Decimal


def compute_debit_credit_ratio(debit: Decimal, credit: Decimal) -> Decimal | None:
    if credit <= 0:
        return None
    return Decimal(str(round(float(debit) / float(credit), 4)))


def compute_profile_completeness(
    *,
    total_movements: int,
    total_amount: Decimal,
    average_amount: Decimal,
    first_seen: date | None,
    last_seen: date | None,
    active_months: int,
    active_days: int,
    monthly_distribution: dict,
    debit_amount: Decimal,
    credit_amount: Decimal,
    related_accounts_count: int,
    related_counterparties_count: int,
    currencies: list,
    journals: dict,
    dimensions_used: list,
) -> Decimal:
    """Fracción de campos de perfil poblados con evidencia real (0–1)."""
    if total_movements <= 0:
        return Decimal("0.0000")

    checks = [
        total_movements > 0,
        total_amount != 0,
        average_amount != 0,
        first_seen is not None,
        last_seen is not None,
        first_seen is not None and last_seen is not None and first_seen <= last_seen,
        active_months > 0,
        active_days > 0,
        bool(monthly_distribution),
        len(monthly_distribution) == active_months,
        debit_amount > 0 or credit_amount > 0,
        related_accounts_count > 0,
        bool(currencies),
        bool(journals.get("distinct_count", 0) if isinstance(journals, dict) else journals),
        bool(dimensions_used),
        related_counterparties_count > 0 or related_accounts_count > 0,
    ]
    score = sum(1 for check in checks if check) / len(checks)
    return Decimal(str(round(score, 4)))
