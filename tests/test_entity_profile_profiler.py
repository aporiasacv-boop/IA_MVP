from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from app.business_entity_profile.metrics import EntityProfileMetrics
from app.business_entity_profile.profiler import EntityProfileGenerator


def test_profiler_run_idempotent_upserts() -> None:
    EntityProfileMetrics.reset_for_tests()
    repo = MagicMock()
    repo.fetch_scalar_aggregates.return_value = [
        {
            "canonical_id": 1,
            "total_movements": 10,
            "total_amount": Decimal("1000"),
            "average_amount": Decimal("100"),
            "first_seen": datetime(2024, 1, 1).date(),
            "last_seen": datetime(2024, 6, 1).date(),
            "active_months": 2,
            "active_days": 20,
            "debit_amount": Decimal("600"),
            "credit_amount": Decimal("400"),
            "related_accounts_count": 2,
            "related_counterparties_count": 1,
            "dimensions_used": ["cuenta_cliente"],
        }
    ]
    repo.fetch_monthly_distributions.return_value = {1: {"2024-01": {"movements": 5, "amount": 500}}}
    repo.fetch_currencies.return_value = {1: ["MXN"]}
    repo.fetch_journals.return_value = {1: {"distinct_count": 1, "top": []}}
    repo.fetch_top_accounts.return_value = {1: []}
    repo.fetch_top_counterparties.return_value = {1: []}
    repo.upsert_profile.return_value = (MagicMock(), False)
    repo.count_profiles.return_value = 1
    repo.average_profile_completeness.return_value = 0.8

    generator = EntityProfileGenerator(repo)
    result = generator.run_idempotent(now=datetime(2026, 6, 24))
    assert result.profiles_upserted == 1
    assert result.profiles_updated == 1
    repo.session.commit.assert_called_once()
