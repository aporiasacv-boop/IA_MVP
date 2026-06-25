from app.business_entity_profile.health import validate_entity_profile_health
from app.business_entity_profile.metrics import EntityProfileMetrics
from app.business_entity_profile.profiler import EntityProfileGenerator
from app.business_entity_profile.repository import BusinessEntityProfileRepository
from app.business_entity_profile.schemas import (
    EntityProfileItem,
    EntityProfileListResponse,
    EntityProfileStatisticsResponse,
    ProfileGenerationResult,
)


class BusinessEntityProfileService:
    def __init__(self, repository: BusinessEntityProfileRepository) -> None:
        self._repository = repository
        self._generator = EntityProfileGenerator(repository)

    def list_profiles(
        self,
        *,
        search: str | None = None,
        sort_by: str = "total_movements",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> EntityProfileListResponse:
        rows, total = self._repository.list_profiles(
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )
        items = [self._to_item(row) for row in rows]
        return EntityProfileListResponse(items=items, total=total, page=page, page_size=page_size)

    def get_profile(self, canonical_id: int) -> EntityProfileItem | None:
        row = self._repository.get_profile_detail(canonical_id)
        return self._to_item(row) if row else None

    def get_statistics(self) -> EntityProfileStatisticsResponse:
        profiles_total = self._repository.count_profiles()
        movements_total = self._repository.sum_total_movements()
        avg_movements = round(movements_total / profiles_total, 2) if profiles_total else 0.0
        return EntityProfileStatisticsResponse(
            entity_profiles_total=profiles_total,
            canonical_entities_total=self._repository.count_canonical(),
            profiles_without_movements=self._repository.count_profiles_without_movements(),
            average_profile_completeness=self._repository.average_profile_completeness(),
            profile_generation_time=EntityProfileMetrics.profile_generation_time,
            last_profile_refresh=self._repository.get_last_refresh()
            or EntityProfileMetrics.last_profile_refresh,
            total_movements_profiled=movements_total,
            average_movements_per_profile=avg_movements,
        )

    def run_generation(self) -> ProfileGenerationResult:
        return self._generator.run_idempotent()

    def validate_health(self) -> dict:
        return validate_entity_profile_health(self._repository.find_health_issues())

    def get_health_issues(self) -> dict[str, list[dict]]:
        return self._repository.find_health_issues()

    def _to_item(self, row: dict) -> EntityProfileItem:
        return EntityProfileItem(
            profile_id=int(row["profile_id"]),
            canonical_id=int(row["canonical_id"]),
            canonical_name=row["canonical_name"],
            primary_rfc=row.get("primary_rfc"),
            total_movements=int(row["total_movements"]),
            total_amount=row["total_amount"],
            average_amount=row["average_amount"],
            first_seen=row.get("first_seen"),
            last_seen=row.get("last_seen"),
            active_months=int(row["active_months"]),
            active_days=int(row["active_days"]),
            debit_amount=row["debit_amount"],
            credit_amount=row["credit_amount"],
            debit_credit_ratio=row.get("debit_credit_ratio"),
            related_accounts_count=int(row["related_accounts_count"]),
            related_counterparties_count=int(row["related_counterparties_count"]),
            monthly_distribution=row.get("monthly_distribution") or {},
            currencies=row.get("currencies") or [],
            journals=row.get("journals") or {},
            dimensions_used=row.get("dimensions_used") or [],
            top_accounts=row.get("top_accounts") or [],
            top_counterparties=row.get("top_counterparties") or [],
            profile_completeness=row["profile_completeness"],
            generated_at=row["generated_at"],
            updated_at=row["updated_at"],
        )
