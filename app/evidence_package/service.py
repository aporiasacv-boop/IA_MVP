import time
from datetime import datetime

from app.evidence_package.constants import EEP_SCHEMA_ID, EEP_VERSION, EXAMPLE_QUESTION, REQUIRED_SECTIONS
from app.evidence_package.evidence_builder import (
    build_evidence_package,
    count_evidence_items,
    package_size_bytes,
)
from app.evidence_package.example_data import build_example_package
from app.evidence_package.health import validate_evidence_health
from app.evidence_package.metrics import EvidencePackageMetrics
from app.evidence_package.repository import EvidencePackageRepository
from app.evidence_package.schemas import (
    EnterpriseEvidencePackage,
    EvidenceBuildRequest,
    EvidenceSchemaResponse,
    EvidenceStatisticsResponse,
)
from app.semantic_intent.execution_planner import build_execution_plan
from app.semantic_intent.semantic_parser import parse_semantic_question


class EvidencePackageService:
    def __init__(self, repository: EvidencePackageRepository) -> None:
        self._repository = repository

    def get_schema(self) -> EvidenceSchemaResponse:
        return EvidenceSchemaResponse(
            schema_id=EEP_SCHEMA_ID,
            schema_version=EEP_VERSION,
            required_sections=sorted(REQUIRED_SECTIONS),
            evidence_item_fields=["key", "value", "source", "evidence", "confidence", "timestamp"],
            description="Enterprise Evidence Package v1 — contrato RAG determinístico sin SQL ni narrativa LLM",
        )

    def build(self, request: EvidenceBuildRequest) -> EnterpriseEvidencePackage:
        started = time.perf_counter()
        parse = parse_semantic_question(request.question)
        plan = build_execution_plan(parse)

        canonical_id = request.canonical_id
        if canonical_id is None:
            canonical_id = self._repository.resolve_canonical_id(plan.entity_hints)
        if canonical_id is None:
            canonical_id = self._repository.fetch_first_available_entity()

        eko = self._repository.fetch_eko(canonical_id) if canonical_id else None
        ero = self._repository.fetch_ero(canonical_id) if canonical_id else None

        package = build_evidence_package(
            question=request.question,
            plan=plan,
            eko=eko,
            ero=ero,
            canonical_id=canonical_id,
            built_at=datetime.now(),
        )

        self._record_metrics(package, plan, eko, ero, time.perf_counter() - started)
        return package

    def get_example(self) -> EnterpriseEvidencePackage:
        canonical_id = self._repository.fetch_first_available_entity()
        if canonical_id:
            return self.build(EvidenceBuildRequest(question=EXAMPLE_QUESTION, canonical_id=canonical_id))
        return build_example_package()

    def get_statistics(self) -> EvidenceStatisticsResponse:
        snap = EvidencePackageMetrics.snapshot()
        return EvidenceStatisticsResponse(**snap)

    def validate_health(self) -> dict:
        return validate_evidence_health(EvidencePackageMetrics.health_issues())

    def get_health_issues(self) -> dict:
        return EvidencePackageMetrics.health_issues()

    def _record_metrics(
        self,
        package: EnterpriseEvidencePackage,
        plan,
        eko,
        ero,
        elapsed: float,
    ) -> None:
        evidence_keys = [item.get("rule_code", item.get("assignment_id", str(i))) for i, item in enumerate(package.evidence)]
        duplicate = len(evidence_keys) != len(set(str(k) for k in evidence_keys))
        inconsistent = any(
            lim.code == "missing_eko" and eko is not None for lim in package.limitations
        ) or any(
            lim.code == "missing_ero" and ero is not None for lim in package.limitations
        )
        conf = float(package.confidence.average_confidence)
        EvidencePackageMetrics.record_build(
            package_id=package.package_id,
            package_size=package_size_bytes(package),
            evidence_items=count_evidence_items(package),
            confidence=conf,
            build_time_seconds=round(elapsed, 4),
            has_evidence=bool(package.evidence),
            missing_eko=eko is None and bool(plan.required_knowledge),
            missing_ero=ero is None and bool(plan.required_reasoning),
            invalid_confidence=conf < 0 or conf > 1,
            duplicate_evidence=duplicate,
            inconsistent_limitations=inconsistent,
        )
