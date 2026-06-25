from app.business_ontology.health import validate_ontology_health
from app.business_ontology.metrics import BusinessOntologyMetrics
from app.business_ontology.ontology_engine import OntologyEngine
from app.business_ontology.repository import BusinessOntologyRepository
from app.business_ontology.schemas import (
    IdentitySummaryItem,
    OntologyAssignmentItem,
    OntologyAssignmentListResponse,
    OntologyEntityView,
    OntologyGenerationResult,
    OntologyListResponse,
    OntologyStatisticsResponse,
    OntologyTypeItem,
    OntologyTypeListResponse,
    ProfileSummaryItem,
)


class BusinessOntologyService:
    def __init__(self, repository: BusinessOntologyRepository) -> None:
        self._repository = repository
        self._engine = OntologyEngine(repository)

    def list_ontology(
        self,
        *,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> OntologyListResponse:
        canonical_ids, total = self._repository.list_ontology_entities(
            search=search, page=page, page_size=page_size
        )
        items = [self._build_entity_view(cid) for cid in canonical_ids]
        return OntologyListResponse(items=items, total=total, page=page, page_size=page_size)

    def list_types(self, *, concept_category: str | None = None) -> OntologyTypeListResponse:
        rows = self._repository.list_types(concept_category=concept_category)
        items = [
            OntologyTypeItem(
                type_id=int(row.type_id),
                concept_category=row.concept_category,
                type_code=row.type_code,
                type_label=row.type_label,
                description=row.description,
                is_active=bool(row.is_active),
                sort_order=int(row.sort_order),
            )
            for row in rows
        ]
        return OntologyTypeListResponse(items=items, total=len(items))

    def list_assignments(
        self,
        *,
        status: str | None = "pending",
        concept_category: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> OntologyAssignmentListResponse:
        rows, total = self._repository.list_assignments(
            status=status,
            concept_category=concept_category,
            page=page,
            page_size=page_size,
        )
        items = [self._to_assignment_item(row) for row in rows]
        return OntologyAssignmentListResponse(items=items, total=total, page=page, page_size=page_size)

    def get_statistics(self) -> OntologyStatisticsResponse:
        return OntologyStatisticsResponse(
            ontology_entities=self._repository.count_entities_with_assignments(),
            ontology_pending=self._repository.count_assignments(status="pending"),
            ontology_approved=self._repository.count_assignments(status="approved"),
            ontology_rejected=self._repository.count_assignments(status="rejected"),
            ontology_rules=self._repository.count_rules(),
            ontology_types=self._repository.count_types(),
            ontology_average_confidence=self._repository.average_confidence(),
            entities_without_suggestions=self._repository.count_entities_without_suggestions(),
            last_ontology_run=BusinessOntologyMetrics.last_ontology_run,
        )

    def run_generation(self) -> OntologyGenerationResult:
        return self._engine.run_idempotent()

    def validate_health(self) -> dict:
        return validate_ontology_health(self._repository.find_health_issues())

    def get_health_issues(self) -> dict[str, list[dict]]:
        return self._repository.find_health_issues()

    def _build_entity_view(self, canonical_id: int) -> OntologyEntityView:
        identity_row = self._repository.get_canonical_identity(canonical_id)
        profile_row = self._repository.get_profile_summary(canonical_id)
        assignments = self._repository.fetch_assignments_for_canonical(canonical_id)
        assignment_items = [self._to_assignment_item(row) for row in assignments]
        top = assignment_items[:5]
        identity = IdentitySummaryItem(
            canonical_id=int(identity_row["canonical_id"]),
            canonical_name=identity_row["canonical_name"],
            primary_rfc=identity_row.get("primary_rfc"),
            normalized_name=identity_row["normalized_name"],
            alias_count=int(identity_row["alias_count"]),
        )
        profile_summary = None
        if profile_row:
            profile_summary = ProfileSummaryItem(**profile_row)
        return OntologyEntityView(
            identity=identity,
            profile_summary=profile_summary,
            assignments=assignment_items,
            top_suggestions=top,
        )

    def _to_assignment_item(self, row: dict) -> OntologyAssignmentItem:
        return OntologyAssignmentItem(
            assignment_id=int(row["assignment_id"]),
            canonical_id=int(row["canonical_id"]),
            concept_category=row["concept_category"],
            type_code=row["type_code"],
            type_label=row["type_label"],
            rule_code=row["rule_code"],
            evidence_json=dict(row.get("evidence_json") or {}),
            score=row["score"],
            confidence=row["confidence"],
            status=row["status"],
            created_at=row["created_at"],
        )
