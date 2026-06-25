from datetime import datetime

from app.enterprise_reasoning.health import validate_reasoning_health
from app.enterprise_reasoning.metrics import EnterpriseReasoningMetrics
from app.enterprise_reasoning.repository import EnterpriseReasoningRepository, ReasoningBuildEngine
from app.enterprise_reasoning.rule_loader import load_enabled_rules, load_rule_packs
from app.enterprise_reasoning.schemas import (
    EnterpriseReasoningObjectSchema,
    ReasoningBuildResult,
    ReasoningObjectListItem,
    ReasoningObjectListResponse,
    ReasoningRulesResponse,
    ReasoningStatisticsResponse,
)


class EnterpriseReasoningService:
    def __init__(self, repository: EnterpriseReasoningRepository) -> None:
        self._repository = repository
        self._engine = ReasoningBuildEngine(repository)

    def list_entities(
        self,
        *,
        search: str | None = None,
        sort_by: str = "average_confidence",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> ReasoningObjectListResponse:
        rows, total = self._repository.list_objects(
            search=search, sort_by=sort_by, sort_dir=sort_dir, page=page, page_size=page_size
        )
        items = [
            ReasoningObjectListItem(
                reasoning_id=int(row["reasoning_id"]),
                canonical_id=int(row["canonical_id"]),
                canonical_name=row["canonical_name"],
                average_confidence=row["average_confidence"],
                findings_count=int(row["findings_count"]),
                alerts_count=int(row["alerts_count"]),
                recommendations_count=int(row["recommendations_count"]),
                built_at=row["built_at"],
            )
            for row in rows
        ]
        return ReasoningObjectListResponse(items=items, total=total, page=page, page_size=page_size)

    def get_entity(self, canonical_id: int) -> EnterpriseReasoningObjectSchema | None:
        obj = self._repository.get_object_by_canonical_id(canonical_id)
        if obj is None:
            return None
        return EnterpriseReasoningObjectSchema.model_validate(obj.reasoning_payload)

    def get_statistics(self) -> ReasoningStatisticsResponse:
        return ReasoningStatisticsResponse(
            reasoning_objects_total=self._repository.count_objects(),
            knowledge_objects_total=self._repository.count_knowledge_objects(),
            reasoning_rules_executed=EnterpriseReasoningMetrics.reasoning_rules_executed,
            average_reasoning_confidence=self._repository.average_confidence(),
            average_findings=self._repository.average_findings(),
            average_alerts=self._repository.average_alerts(),
            average_recommendations=self._repository.average_recommendations(),
            last_reasoning_refresh=self._repository.get_last_refresh()
            or EnterpriseReasoningMetrics.last_reasoning_refresh,
            incomplete_objects=self._repository.count_incomplete(),
        )

    def get_rules(self) -> ReasoningRulesResponse:
        packs = load_rule_packs()
        all_rules = [rule for pack in packs for rule in pack.rules]
        enabled = [rule for rule in all_rules if rule.enabled]
        return ReasoningRulesResponse(packs=packs, total_rules=len(all_rules), enabled_rules=len(enabled))

    def run_build(self) -> ReasoningBuildResult:
        result = self._engine.run_idempotent()
        EnterpriseReasoningMetrics.record_run(
            objects_total=self._repository.count_objects(),
            rules_executed=result["rules_executed"],
            average_confidence=self._repository.average_confidence(),
            average_findings=self._repository.average_findings(),
            average_alerts=self._repository.average_alerts(),
            average_recommendations=self._repository.average_recommendations(),
            build_time_seconds=result["build_time_seconds"],
            run_at=self._repository.get_last_refresh() or datetime.now(),
        )
        return ReasoningBuildResult(**result)

    def validate_health(self) -> dict:
        return validate_reasoning_health(self._repository.find_health_issues())

    def get_health_issues(self) -> dict[str, list[dict]]:
        return self._repository.find_health_issues()
