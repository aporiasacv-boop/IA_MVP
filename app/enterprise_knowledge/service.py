from datetime import datetime

from app.enterprise_knowledge.constants import EKO_SCHEMA_ID, EKO_VERSION, REQUIRED_SECTIONS
from app.enterprise_knowledge.health import validate_knowledge_health
from app.enterprise_knowledge.metrics import EnterpriseKnowledgeMetrics
from app.enterprise_knowledge.repository import EnterpriseKnowledgeRepository, KnowledgeBuildEngine
from app.enterprise_knowledge.schemas import (
    EnterpriseKnowledgeObjectSchema,
    KnowledgeBuildResult,
    KnowledgeObjectListItem,
    KnowledgeObjectListResponse,
    KnowledgeSchemaResponse,
    KnowledgeStatisticsResponse,
)


class EnterpriseKnowledgeService:
    def __init__(self, repository: EnterpriseKnowledgeRepository) -> None:
        self._repository = repository
        self._engine = KnowledgeBuildEngine(repository)

    def list_entities(
        self,
        *,
        search: str | None = None,
        sort_by: str = "completeness",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> KnowledgeObjectListResponse:
        rows, total = self._repository.list_objects(
            search=search, sort_by=sort_by, sort_dir=sort_dir, page=page, page_size=page_size
        )
        items = [
            KnowledgeObjectListItem(
                knowledge_id=int(row["knowledge_id"]),
                canonical_id=int(row["canonical_id"]),
                canonical_name=row["canonical_name"],
                completeness=row["completeness"],
                average_confidence=row["average_confidence"],
                built_at=row["built_at"],
            )
            for row in rows
        ]
        return KnowledgeObjectListResponse(items=items, total=total, page=page, page_size=page_size)

    def get_entity(self, canonical_id: int) -> EnterpriseKnowledgeObjectSchema | None:
        obj = self._repository.get_object_by_canonical_id(canonical_id)
        if obj is None:
            return None
        return EnterpriseKnowledgeObjectSchema.model_validate(obj.knowledge_payload)

    def get_statistics(self) -> KnowledgeStatisticsResponse:
        return KnowledgeStatisticsResponse(
            knowledge_objects_total=self._repository.count_objects(),
            canonical_entities_total=self._repository.count_canonical(),
            knowledge_build_time=EnterpriseKnowledgeMetrics.knowledge_build_time,
            knowledge_average_completeness=self._repository.average_completeness(),
            knowledge_average_confidence=self._repository.average_confidence(),
            knowledge_last_refresh=self._repository.get_last_refresh()
            or EnterpriseKnowledgeMetrics.knowledge_last_refresh,
            incomplete_objects=self._repository.count_incomplete(),
        )

    def get_schema(self) -> KnowledgeSchemaResponse:
        return KnowledgeSchemaResponse(
            schema_id=EKO_SCHEMA_ID,
            schema_version=EKO_VERSION,
            required_sections=sorted(REQUIRED_SECTIONS),
            knowledge_item_fields=["key", "value", "source", "evidence", "confidence", "computed_at"],
            description="Enterprise Knowledge Object v1 — contrato determinístico sin SQL ni narrativa LLM",
        )

    def run_build(self) -> KnowledgeBuildResult:
        result = self._engine.run_idempotent()
        EnterpriseKnowledgeMetrics.record_run(
            objects_total=self._repository.count_objects(),
            build_time_seconds=result["build_time_seconds"],
            average_completeness=self._repository.average_completeness(),
            average_confidence=self._repository.average_confidence(),
            run_at=self._repository.get_last_refresh() or datetime.now(),
        )
        return KnowledgeBuildResult(**result)

    def validate_health(self) -> dict:
        return validate_knowledge_health(self._repository.find_health_issues())

    def get_health_issues(self) -> dict[str, list[dict]]:
        return self._repository.find_health_issues()
