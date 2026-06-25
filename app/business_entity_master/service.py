from app.business_entity_master.health import (
    BusinessEntityMasterHealthError,
    validate_entity_master_health,
)
from app.business_entity_master.loader import BusinessEntityMasterLoader
from app.business_entity_master.metrics import BusinessEntityMasterMetrics
from app.business_entity_master.repository import BusinessEntityMasterRepository
from app.business_entity_master.schemas import (
    BusinessEntityItem,
    BusinessEntityListResponse,
    BusinessEntityStatisticsResponse,
    EntityLoadResult,
)
from app.models.business_entity_master import BusinessEntityMaster


class BusinessEntityMasterService:
    def __init__(self, repository: BusinessEntityMasterRepository) -> None:
        self._repository = repository
        self._loader = BusinessEntityMasterLoader(repository)

    def list_entities(
        self,
        *,
        search: str | None = None,
        source_column: str | None = None,
        classification_status: str | None = None,
        sort_by: str = "movement_count",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> BusinessEntityListResponse:
        rows, total = self._repository.list_entities(
            search=search,
            source_column=source_column,
            classification_status=classification_status,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )
        return BusinessEntityListResponse(
            items=[self._to_item(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_by_code(
        self,
        entity_code: str,
        *,
        source_column: str | None = None,
    ) -> list[BusinessEntityItem]:
        rows = self._repository.get_by_code(entity_code, source_column=source_column)
        return [self._to_item(row) for row in rows]

    def get_statistics(self) -> BusinessEntityStatisticsResponse:
        total = self._repository.count_all()
        duplicated = self._repository.count_duplicated_codes()
        by_source, by_status = self._repository.get_statistics_breakdown()
        metrics = BusinessEntityMasterMetrics.snapshot(total=total)
        return BusinessEntityStatisticsResponse(
            business_entities_total=total,
            business_entities_loaded=metrics["business_entities_loaded"],
            duplicated_entities=duplicated,
            last_entity_refresh=metrics["last_entity_refresh"],
            by_source_column=by_source,
            by_classification_status=by_status,
        )

    def load_idempotent(self, *, csv_path=None) -> EntityLoadResult:
        return self._loader.load_idempotent(csv_path=csv_path)

    def validate_health(self) -> dict:
        issues = self._repository.find_health_issues()
        return validate_entity_master_health(issues)

    def get_health_issues(self) -> dict[str, list[dict]]:
        return self._repository.find_health_issues()

    @staticmethod
    def _to_item(row: BusinessEntityMaster) -> BusinessEntityItem:
        return BusinessEntityItem(
            entity_id=row.entity_id,
            entity_code=row.entity_code,
            entity_name=row.entity_name,
            source_system=row.source_system,
            source_table=row.source_table,
            source_column=row.source_column,
            movement_count=int(row.movement_count),
            movement_amount=row.movement_amount,
            first_seen=row.first_seen,
            last_seen=row.last_seen,
            classification_status=row.classification_status,
            confidence=row.confidence,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
