from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.business_entity_profile.health import EntityProfileHealthError
from app.business_entity_profile.metrics import EntityProfileMetrics
from app.business_entity_profile.repository import BusinessEntityProfileRepository
from app.business_entity_profile.service import BusinessEntityProfileService


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    EntityProfileMetrics.reset_for_tests()


def test_service_list_profiles() -> None:
    repo = MagicMock(spec=BusinessEntityProfileRepository)
    repo.list_profiles.return_value = (
        [
            {
                "profile_id": 1,
                "canonical_id": 10,
                "canonical_name": "WALMART",
                "primary_rfc": None,
                "total_movements": 50,
                "total_amount": Decimal("1000"),
                "average_amount": Decimal("20"),
                "first_seen": date(2024, 1, 1),
                "last_seen": date(2024, 6, 1),
                "active_months": 6,
                "active_days": 100,
                "debit_amount": Decimal("600"),
                "credit_amount": Decimal("400"),
                "debit_credit_ratio": Decimal("1.5"),
                "related_accounts_count": 2,
                "related_counterparties_count": 1,
                "monthly_distribution": {},
                "currencies": ["MXN"],
                "journals": {},
                "dimensions_used": ["cuenta_cliente"],
                "top_accounts": [],
                "top_counterparties": [],
                "profile_completeness": Decimal("0.8"),
                "generated_at": datetime(2026, 6, 24),
                "updated_at": datetime(2026, 6, 24),
            }
        ],
        1,
    )
    service = BusinessEntityProfileService(repo)
    response = service.list_profiles()
    assert response.total == 1
    assert response.items[0].canonical_name == "WALMART"


def test_service_get_profile_not_found() -> None:
    repo = MagicMock(spec=BusinessEntityProfileRepository)
    repo.get_profile_detail.return_value = None
    service = BusinessEntityProfileService(repo)
    assert service.get_profile(999) is None


def test_service_get_statistics() -> None:
    repo = MagicMock(spec=BusinessEntityProfileRepository)
    repo.count_profiles.return_value = 100
    repo.count_canonical.return_value = 100
    repo.count_profiles_without_movements.return_value = 5
    repo.average_profile_completeness.return_value = 0.75
    repo.sum_total_movements.return_value = 5000
    repo.get_last_refresh.return_value = datetime(2026, 6, 24)
    service = BusinessEntityProfileService(repo)
    stats = service.get_statistics()
    assert stats.entity_profiles_total == 100
    assert stats.average_movements_per_profile == 50.0


def test_service_validate_health_ok() -> None:
    repo = MagicMock(spec=BusinessEntityProfileRepository)
    repo.find_health_issues.return_value = {
        "inconsistent_amounts": [],
        "invalid_dates": [],
        "incomplete_distributions": [],
        "profiles_without_movements": [],
        "entities_without_relations": [],
    }
    service = BusinessEntityProfileService(repo)
    assert service.validate_health()["status"] == "healthy"


def test_service_validate_health_raises() -> None:
    repo = MagicMock(spec=BusinessEntityProfileRepository)
    repo.find_health_issues.return_value = {
        "inconsistent_amounts": [{"profile_id": 1}],
        "invalid_dates": [],
        "incomplete_distributions": [],
        "profiles_without_movements": [],
        "entities_without_relations": [],
    }
    service = BusinessEntityProfileService(repo)
    with pytest.raises(EntityProfileHealthError):
        service.validate_health()


def test_service_run_generation() -> None:
    repo = MagicMock(spec=BusinessEntityProfileRepository)
    service = BusinessEntityProfileService(repo)
    service._generator.run_idempotent = MagicMock(
        return_value=MagicMock(
            profiles_upserted=10,
            profiles_created=2,
            profiles_updated=8,
            generation_time_seconds=1.5,
        )
    )
    result = service.run_generation()
    assert result.profiles_upserted == 10


def test_service_get_health_issues() -> None:
    repo = MagicMock(spec=BusinessEntityProfileRepository)
    repo.find_health_issues.return_value = {"inconsistent_amounts": []}
    service = BusinessEntityProfileService(repo)
    assert service.get_health_issues() == {"inconsistent_amounts": []}
