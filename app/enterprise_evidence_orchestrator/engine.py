import time
from typing import Any

from app.capability_plan_executor.schemas import CapabilityQueryRunner
from app.core.settings import settings
from app.enterprise_evidence_orchestrator.constants import (
    MIN_EVIDENCE_ITEMS,
    MIN_PACKAGE_COVERAGE,
    ORCHESTRATOR_SKIP_QUESTION_PATTERNS,
    SKIP_FALLBACK_TYPES,
    SOURCE_BUSINESS_PIPELINE,
)
from app.query_engine.query_types import BusinessQueryType
from app.utils.text_normalizer import normalize_for_matching
from app.enterprise_evidence_orchestrator.metrics import record_orchestration
from app.enterprise_evidence_orchestrator.schemas import (
    CollectedEvidenceItem,
    EnterpriseEvidencePackage,
)
from app.enterprise_evidence_planner.schemas import EnterpriseEvidencePlan, EvidenceItem
from app.schemas.hybrid_chat import HybridChatResult


class EnterpriseEvidenceOrchestrator:
    """Ejecuta el plan de evidencia vía Runtime inyectado. No altera la respuesta visible."""

    def __init__(
        self,
        *,
        execute_capability: CapabilityQueryRunner,
        enabled: bool | None = None,
    ) -> None:
        self._execute_capability = execute_capability
        self._enabled = (
            settings.ENTERPRISE_EVIDENCE_ORCHESTRATOR_ENABLED if enabled is None else enabled
        )

    def orchestrate(
        self,
        *,
        question: str,
        session_id: str | None,
        result: HybridChatResult,
    ) -> HybridChatResult:
        if not self._enabled:
            return result

        plan = _parse_evidence_plan(result.metadata)
        if not _should_orchestrate(plan, result, question):
            record_orchestration(built_package=False, partial=False)
            return result

        started = time.perf_counter()
        executed: list[str] = []
        completed: list[str] = []
        failed: list[str] = []
        collected: list[CollectedEvidenceItem] = []
        capability_cache: dict[str, HybridChatResult] = {}

        for capability in plan.execution_order:
            executed.append(capability)
            try:
                if capability in capability_cache:
                    pipeline_result = capability_cache[capability]
                else:
                    pipeline_result = self._execute_capability(capability, session_id)
                    capability_cache[capability] = pipeline_result

                if pipeline_result.handled_by != "business_pipeline" or not pipeline_result.success:
                    failed.append(capability)
                    continue

                completed.append(capability)
                for evidence in _evidence_items_for_capability(plan, capability):
                    collected.append(_to_collected_evidence(evidence, pipeline_result))
            except Exception:
                failed.append(capability)

        if not collected:
            record_orchestration(built_package=False, partial=False)
            return HybridChatResult(
                handled_by=result.handled_by,
                success=result.success,
                answer=result.answer,
                suggestions=result.suggestions,
                metadata={
                    **result.metadata,
                    "executed_capabilities": executed,
                    "completed_capabilities": completed,
                    "failed_capabilities": failed,
                    "total_execution_time_ms": round((time.perf_counter() - started) * 1000, 2),
                    "evidence_count": 0,
                    "package_coverage": 0.0,
                },
            )

        package = _build_package(plan, collected, executed, completed, failed)
        partial = bool(failed) or len(completed) < len(executed)
        record_orchestration(built_package=True, partial=partial)

        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={
                **result.metadata,
                **package.observability_metadata(
                    executed_capabilities=executed,
                    completed_capabilities=completed,
                    failed_capabilities=failed,
                    total_execution_time_ms=(time.perf_counter() - started) * 1000,
                ),
            },
        )


def _should_orchestrate(
    plan: EnterpriseEvidencePlan,
    result: HybridChatResult,
    question: str,
) -> bool:
    if not plan.execution_order:
        return False
    if plan.estimated_coverage < MIN_PACKAGE_COVERAGE:
        return False
    if len(plan.required_evidence) < MIN_EVIDENCE_ITEMS:
        return False

    fallback_type = str(result.metadata.get("fallback_type", ""))
    if fallback_type in SKIP_FALLBACK_TYPES:
        return False

    normalized = normalize_for_matching(question)
    if any(pattern in normalized for pattern in ORCHESTRATOR_SKIP_QUESTION_PATTERNS):
        return False

    if (
        result.handled_by == "guided_fallback"
        and fallback_type == "UNKNOWN"
        and plan.required_capabilities == [BusinessQueryType.KPIS.value]
    ):
        return False

    return True


def _parse_evidence_plan(metadata: dict[str, Any]) -> EnterpriseEvidencePlan:
    raw = metadata.get("enterprise_evidence_plan")
    if isinstance(raw, dict):
        return EnterpriseEvidencePlan.model_validate(raw)
    return EnterpriseEvidencePlan(
        business_goal=str(metadata.get("business_goal", "")),
        required_evidence=list(metadata.get("required_evidence", [])),
        required_capabilities=list(metadata.get("required_capabilities", [])),
        execution_order=list(metadata.get("execution_order", [])),
        estimated_coverage=float(metadata.get("estimated_coverage", 0)),
        missing_evidence=list(metadata.get("missing_evidence", [])),
    )


def _evidence_items_for_capability(
    plan: EnterpriseEvidencePlan,
    capability: str,
) -> list[EvidenceItem]:
    return [item for item in plan.evidence_items if item.capability == capability]


def _to_collected_evidence(
    evidence: EvidenceItem,
    pipeline_result: HybridChatResult,
) -> CollectedEvidenceItem:
    query_type = str(pipeline_result.metadata.get("query_type", evidence.capability))
    confidence = pipeline_result.metadata.get("confidence")
    return CollectedEvidenceItem(
        evidence_id=evidence.evidence_id,
        evidence_label=evidence.label,
        capability=evidence.capability,
        query_type=query_type,
        source=SOURCE_BUSINESS_PIPELINE,
        answer=pipeline_result.answer,
        confidence=float(confidence) if isinstance(confidence, (int, float)) else None,
        success=pipeline_result.success,
    )


def _build_package(
    plan: EnterpriseEvidencePlan,
    collected: list[CollectedEvidenceItem],
    executed: list[str],
    completed: list[str],
    failed: list[str],
) -> EnterpriseEvidencePackage:
    confidences = [item.confidence for item in collected if item.confidence is not None]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    unique_query_types = list(dict.fromkeys(item.query_type for item in collected))
    unique_sources = list(dict.fromkeys(item.source for item in collected))
    coverage = _package_coverage(plan, len(collected), len(completed), len(executed))

    return EnterpriseEvidencePackage(
        business_goal=plan.business_goal,
        evidence_items=collected,
        coverage=coverage,
        sources=unique_sources,
        query_types=unique_query_types,
        execution_summary=(
            f"{len(completed)}/{len(executed)} capabilities completadas; "
            f"{len(collected)} evidencias recolectadas."
        ),
        missing_evidence=list(plan.missing_evidence) + [
            cap for cap in failed if cap not in plan.missing_evidence
        ],
        confidence=round(avg_confidence, 4),
    )


def _package_coverage(
    plan: EnterpriseEvidencePlan,
    collected_count: int,
    completed_count: int,
    executed_count: int,
) -> float:
    if executed_count == 0:
        return 0.0
    execution_ratio = completed_count / executed_count
    evidence_ratio = collected_count / max(len(plan.required_evidence), 1)
    return min(96.0, round(plan.estimated_coverage * min(execution_ratio, evidence_ratio), 1))
