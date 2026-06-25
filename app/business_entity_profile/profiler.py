import time
from datetime import datetime
from decimal import Decimal

from app.business_entity_profile.completeness import compute_debit_credit_ratio, compute_profile_completeness
from app.business_entity_profile.metrics import EntityProfileMetrics
from app.business_entity_profile.repository import BusinessEntityProfileRepository
from app.business_entity_profile.schemas import ProfileGenerationResult


class EntityProfileGenerator:
    def __init__(self, repository: BusinessEntityProfileRepository) -> None:
        self._repository = repository

    def run_idempotent(self, *, now: datetime | None = None) -> ProfileGenerationResult:
        started = time.perf_counter()
        timestamp = now or datetime.now()
        created = 0
        updated = 0

        scalar_rows = self._repository.fetch_scalar_aggregates()
        monthly_map = self._repository.fetch_monthly_distributions()
        currencies_map = self._repository.fetch_currencies()
        journals_map = self._repository.fetch_journals()
        top_accounts_map = self._repository.fetch_top_accounts()
        top_counterparties_map = self._repository.fetch_top_counterparties()

        for row in scalar_rows:
            canonical_id = int(row["canonical_id"])
            total_movements = int(row["total_movements"] or 0)
            total_amount = Decimal(str(row["total_amount"] or 0))
            average_amount = Decimal(str(row["average_amount"] or 0))
            debit_amount = Decimal(str(row["debit_amount"] or 0))
            credit_amount = Decimal(str(row["credit_amount"] or 0))
            monthly_distribution = monthly_map.get(canonical_id, {})
            currencies = currencies_map.get(canonical_id, [])
            journals = journals_map.get(canonical_id, {"distinct_count": 0, "top": []})
            dimensions_raw = row.get("dimensions_used") or []
            dimensions_used = list(dimensions_raw) if isinstance(dimensions_raw, list) else []
            top_accounts = top_accounts_map.get(canonical_id, [])
            top_counterparties = top_counterparties_map.get(canonical_id, [])

            completeness = compute_profile_completeness(
                total_movements=total_movements,
                total_amount=total_amount,
                average_amount=average_amount,
                first_seen=row.get("first_seen"),
                last_seen=row.get("last_seen"),
                active_months=int(row["active_months"] or 0),
                active_days=int(row["active_days"] or 0),
                monthly_distribution=monthly_distribution,
                debit_amount=debit_amount,
                credit_amount=credit_amount,
                related_accounts_count=int(row["related_accounts_count"] or 0),
                related_counterparties_count=int(row["related_counterparties_count"] or 0),
                currencies=currencies,
                journals=journals,
                dimensions_used=dimensions_used,
            )

            _, is_new = self._repository.upsert_profile(
                canonical_id=canonical_id,
                total_movements=total_movements,
                total_amount=total_amount,
                average_amount=average_amount,
                first_seen=row.get("first_seen"),
                last_seen=row.get("last_seen"),
                active_months=int(row["active_months"] or 0),
                active_days=int(row["active_days"] or 0),
                debit_amount=debit_amount,
                credit_amount=credit_amount,
                debit_credit_ratio=compute_debit_credit_ratio(debit_amount, credit_amount),
                related_accounts_count=int(row["related_accounts_count"] or 0),
                related_counterparties_count=int(row["related_counterparties_count"] or 0),
                monthly_distribution=monthly_distribution,
                currencies=currencies,
                journals=journals,
                dimensions_used=dimensions_used,
                top_accounts=top_accounts,
                top_counterparties=top_counterparties,
                profile_completeness=completeness,
                generated_at=timestamp,
            )
            if is_new:
                created += 1
            else:
                updated += 1

        self._repository.session.commit()
        elapsed = round(time.perf_counter() - started, 4)
        EntityProfileMetrics.record_run(
            profiles_total=self._repository.count_profiles(),
            average_completeness=self._repository.average_profile_completeness(),
            generation_time_seconds=elapsed,
            run_at=timestamp,
        )
        return ProfileGenerationResult(
            profiles_upserted=created + updated,
            profiles_created=created,
            profiles_updated=updated,
            generation_time_seconds=elapsed,
        )
