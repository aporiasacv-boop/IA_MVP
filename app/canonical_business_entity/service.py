from app.canonical_business_entity.health import (
    CanonicalEntityHealthError,
    validate_canonical_health,
)
from app.canonical_business_entity.metrics import CanonicalEntityMetrics
from app.canonical_business_entity.repository import CanonicalBusinessEntityRepository
from app.canonical_business_entity.schemas import (
    CanonicalEntityItem,
    CanonicalEntityListResponse,
    CanonicalStatisticsResponse,
    CanonicalSuggestionItem,
    CanonicalSuggestionListResponse,
    EntityAliasItem,
    SuggestionEntityRef,
    SuggestionRunResult,
)
from app.canonical_business_entity.suggestion_engine import CanonicalSuggestionEngine
from app.models.canonical_business_entity import CanonicalBusinessEntity


class CanonicalBusinessEntityService:
    def __init__(self, repository: CanonicalBusinessEntityRepository) -> None:
        self._repository = repository
        self._engine = CanonicalSuggestionEngine(repository)

    def list_canonical(
        self,
        *,
        search: str | None = None,
        sort_by: str = "alias_count",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> CanonicalEntityListResponse:
        rows, total = self._repository.list_canonical(
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )
        items = [self._to_canonical_item(row, include_aliases=True) for row in rows]
        return CanonicalEntityListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def list_suggestions(
        self,
        *,
        status: str | None = "pending",
        min_score: float | None = None,
        page: int = 1,
        page_size: int = 50,
        sort_dir: str = "desc",
    ) -> CanonicalSuggestionListResponse:
        rows, total = self._repository.list_suggestions(
            status=status,
            min_score=min_score,
            page=page,
            page_size=page_size,
            sort_dir=sort_dir,
        )
        items = [
            CanonicalSuggestionItem(
                suggestion_id=int(row["suggestion_id"]),
                source_entity=SuggestionEntityRef(
                    entity_id=int(row["source_entity_id"]),
                    entity_code=row["source_entity_code"],
                    entity_name=row["source_entity_name"],
                    source_column=row["source_source_column"],
                ),
                candidate_entity=SuggestionEntityRef(
                    entity_id=int(row["candidate_entity_id"]),
                    entity_code=row["candidate_entity_code"],
                    entity_name=row["candidate_entity_name"],
                    source_column=row["candidate_source_column"],
                ),
                rule_used=row["rule_used"],
                score=row["score"],
                status=row["status"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
        return CanonicalSuggestionListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_statistics(self) -> CanonicalStatisticsResponse:
        commercial_total = self._repository.count_commercial_entities()
        resolved = self._repository.count_resolved_commercial()
        unresolved = max(commercial_total - resolved, 0)
        unresolved_pct = round((unresolved / commercial_total) * 100, 2) if commercial_total else 0.0
        orphans = len(self._repository.get_unresolved_commercial_entity_ids())
        return CanonicalStatisticsResponse(
            canonical_entities_total=self._repository.count_canonical(),
            canonical_matches=self._repository.count_canonical_matches(),
            pending_matches=self._repository.count_pending_suggestions(),
            automatic_suggestions=self._repository.count_automatic_suggestions(),
            commercial_entities_total=commercial_total,
            resolved_entities=resolved,
            unresolved_entities=unresolved,
            unresolved_pct=unresolved_pct,
            orphan_entities=orphans,
            last_suggestion_run=CanonicalEntityMetrics.last_suggestion_run,
        )

    def run_suggestions(self) -> SuggestionRunResult:
        return self._engine.run_idempotent()

    def validate_health(self) -> dict:
        return validate_canonical_health(self._repository.find_health_issues())

    def get_health_issues(self) -> dict[str, list[dict]]:
        return self._repository.find_health_issues()

    def _to_canonical_item(
        self,
        row: CanonicalBusinessEntity,
        *,
        include_aliases: bool,
    ) -> CanonicalEntityItem:
        aliases: list[EntityAliasItem] = []
        if include_aliases:
            alias_rows = self._repository.list_aliases_for_canonical(int(row.canonical_id))
            aliases = [
                EntityAliasItem(
                    entity_id=int(item["entity_id"]),
                    entity_code=item["entity_code"],
                    entity_name=item["entity_name"],
                    source_column=item["source_column"],
                    resolution_rule=item["resolution_rule"],
                    resolution_score=item["resolution_score"],
                )
                for item in alias_rows
            ]
        return CanonicalEntityItem(
            canonical_id=int(row.canonical_id),
            canonical_name=row.canonical_name,
            normalized_name=row.normalized_name,
            primary_rfc=row.primary_rfc,
            alias_count=int(row.alias_count),
            aliases=aliases,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
