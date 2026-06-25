from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.business_entity_profile.metrics import EntityProfileMetrics
from app.business_entity_profile.repository import BusinessEntityProfileRepository
from app.models.business_entity_profile import BusinessEntityProfile


def _scalar_session(return_value):
    session = MagicMock(spec=Session)
    session.scalar.return_value = return_value
    return session


def test_count_profiles_returns_zero() -> None:
    repo = BusinessEntityProfileRepository(_scalar_session(0))
    assert repo.count_profiles() == 0


def test_average_profile_completeness() -> None:
    repo = BusinessEntityProfileRepository(_scalar_session(0.85))
    assert repo.average_profile_completeness() == 0.85


def test_upsert_profile_creates_new() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = None
    repo = BusinessEntityProfileRepository(session)
    profile, is_new = repo.upsert_profile(
        canonical_id=1,
        total_movements=10,
        total_amount=Decimal("1000"),
        average_amount=Decimal("100"),
        first_seen=date(2024, 1, 1),
        last_seen=date(2024, 6, 1),
        active_months=2,
        active_days=20,
        debit_amount=Decimal("600"),
        credit_amount=Decimal("400"),
        debit_credit_ratio=Decimal("1.5"),
        related_accounts_count=3,
        related_counterparties_count=2,
        monthly_distribution={"2024-01": {"movements": 5, "amount": 500}},
        currencies=["MXN"],
        journals={"distinct_count": 1, "top": []},
        dimensions_used=["cuenta_cliente"],
        top_accounts=[],
        top_counterparties=[],
        profile_completeness=Decimal("0.8000"),
        generated_at=datetime(2026, 6, 24),
    )
    assert is_new is True
    session.add.assert_called_once()
    assert profile.canonical_id == 1


def test_upsert_profile_updates_existing() -> None:
    existing = BusinessEntityProfile(
        profile_id=1,
        canonical_id=1,
        total_movements=5,
        total_amount=Decimal("500"),
        average_amount=Decimal("100"),
        first_seen=date(2024, 1, 1),
        last_seen=date(2024, 3, 1),
        active_months=1,
        active_days=10,
        debit_amount=Decimal("300"),
        credit_amount=Decimal("200"),
        debit_credit_ratio=Decimal("1.5"),
        related_accounts_count=1,
        related_counterparties_count=0,
        monthly_distribution={},
        currencies=[],
        journals={},
        dimensions_used=[],
        top_accounts=[],
        top_counterparties=[],
        profile_completeness=Decimal("0.5"),
        generated_at=datetime(2026, 1, 1),
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    session = MagicMock(spec=Session)
    session.scalar.return_value = existing
    repo = BusinessEntityProfileRepository(session)
    profile, is_new = repo.upsert_profile(
        canonical_id=1,
        total_movements=20,
        total_amount=Decimal("2000"),
        average_amount=Decimal("100"),
        first_seen=date(2024, 1, 1),
        last_seen=date(2024, 12, 1),
        active_months=3,
        active_days=30,
        debit_amount=Decimal("1200"),
        credit_amount=Decimal("800"),
        debit_credit_ratio=Decimal("1.5"),
        related_accounts_count=2,
        related_counterparties_count=1,
        monthly_distribution={"2024-01": {}},
        currencies=["MXN"],
        journals={"distinct_count": 2, "top": []},
        dimensions_used=["cuenta_proveedor"],
        top_accounts=[],
        top_counterparties=[],
        profile_completeness=Decimal("0.9"),
        generated_at=datetime(2026, 6, 24),
    )
    assert is_new is False
    assert profile.total_movements == 20


def test_list_profiles_reads_sql() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.scalar_one.return_value = 1
    session.execute.return_value.mappings.return_value.all.return_value = [
        {
            "profile_id": 1,
            "canonical_id": 10,
            "canonical_name": "WALMART",
            "primary_rfc": "NWM9709244",
            "total_movements": 100,
            "total_amount": Decimal("50000"),
            "average_amount": Decimal("500"),
            "first_seen": date(2024, 1, 1),
            "last_seen": date(2024, 12, 1),
            "active_months": 12,
            "active_days": 200,
            "debit_amount": Decimal("30000"),
            "credit_amount": Decimal("20000"),
            "debit_credit_ratio": Decimal("1.5"),
            "related_accounts_count": 5,
            "related_counterparties_count": 3,
            "monthly_distribution": {},
            "currencies": ["MXN"],
            "journals": {"distinct_count": 10, "top": []},
            "dimensions_used": ["cuenta_cliente"],
            "top_accounts": [],
            "top_counterparties": [],
            "profile_completeness": Decimal("0.85"),
            "generated_at": datetime(2026, 6, 24),
            "updated_at": datetime(2026, 6, 24),
        }
    ]
    repo = BusinessEntityProfileRepository(session)
    rows, total = repo.list_profiles(search="walmart")
    assert total == 1
    assert rows[0]["canonical_name"] == "WALMART"


def test_count_canonical_and_without_movements() -> None:
    session = MagicMock(spec=Session)
    session.scalar.side_effect = [800, 12, 50000]
    repo = BusinessEntityProfileRepository(session)
    assert repo.count_canonical() == 800
    assert repo.count_profiles_without_movements() == 12
    assert repo.sum_total_movements() == 50000


def test_list_canonical_ids() -> None:
    session = MagicMock(spec=Session)
    session.scalars.return_value.all.return_value = [1, 2, 3]
    repo = BusinessEntityProfileRepository(session)
    assert repo.list_canonical_ids() == [1, 2, 3]


def test_fetch_scalar_aggregates_executes_sql() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.return_value = [
        {"canonical_id": 1, "total_movements": 5}
    ]
    repo = BusinessEntityProfileRepository(session)
    rows = repo.fetch_scalar_aggregates()
    assert rows[0]["canonical_id"] == 1


def test_fetch_monthly_distributions() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.return_value = [
        {"canonical_id": 1, "monthly_distribution": {"2024-01": {"movements": 3}}}
    ]
    repo = BusinessEntityProfileRepository(session)
    result = repo.fetch_monthly_distributions()
    assert "2024-01" in result[1]


def test_fetch_currencies() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.return_value = [
        {"canonical_id": 1, "currencies": ["MXN", "USD"]}
    ]
    repo = BusinessEntityProfileRepository(session)
    assert repo.fetch_currencies()[1] == ["MXN", "USD"]


def test_fetch_journals() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.return_value = [
        {"canonical_id": 1, "distinct_count": 2, "top": [{"numero": "GJ-1", "movements": 5}]}
    ]
    repo = BusinessEntityProfileRepository(session)
    journals = repo.fetch_journals()[1]
    assert journals["distinct_count"] == 2


def test_fetch_top_accounts_and_counterparties() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.side_effect = [
        [{"canonical_id": 1, "top_accounts": [{"code": "20101", "name": "X", "movements": 1, "amount": 10}]}],
        [{"canonical_id": 1, "top_counterparties": [{"code": "C1", "name": "Y", "dimension": "cuenta_cliente", "movements": 2, "amount": 20}]}],
    ]
    repo = BusinessEntityProfileRepository(session)
    assert repo.fetch_top_accounts()[1][0]["code"] == "20101"
    assert repo.fetch_top_counterparties()[1][0]["code"] == "C1"


def test_get_profile_by_canonical_id() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = MagicMock(canonical_id=1)
    repo = BusinessEntityProfileRepository(session)
    assert repo.get_profile_by_canonical_id(1) is not None


def test_get_profile_detail() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.first.return_value = {"canonical_id": 1, "canonical_name": "X"}
    repo = BusinessEntityProfileRepository(session)
    assert repo.get_profile_detail(1)["canonical_name"] == "X"


def test_find_health_issues() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.side_effect = [
        [],
        [],
        [],
        [{"profile_id": 1}],
        [],
    ]
    repo = BusinessEntityProfileRepository(session)
    issues = repo.find_health_issues()
    assert len(issues["profiles_without_movements"]) == 1
