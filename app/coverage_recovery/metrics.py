from dataclasses import dataclass

from app.coverage_recovery.classifier import RecoveryCategory, classify_recovery_question
from app.schemas.hybrid_chat import HybridChatResult


@dataclass
class CoverageRecoveryMetricsState:
    coverage_recovery_hits: int = 0
    coverage_recovery_misses: int = 0


coverage_recovery_metrics = CoverageRecoveryMetricsState()


class CoverageRecoveryMetricsService:
    @staticmethod
    def record_hit() -> None:
        coverage_recovery_metrics.coverage_recovery_hits += 1

    @staticmethod
    def record_miss() -> None:
        coverage_recovery_metrics.coverage_recovery_misses += 1

    @staticmethod
    def snapshot() -> dict[str, int]:
        return {
            "coverage_recovery_hits": coverage_recovery_metrics.coverage_recovery_hits,
            "coverage_recovery_misses": coverage_recovery_metrics.coverage_recovery_misses,
        }

    @staticmethod
    def record_outcome(question: str, result: HybridChatResult) -> None:
        category = classify_recovery_question(question)
        if category is None:
            return
        if _is_recovery_hit(category, result):
            CoverageRecoveryMetricsService.record_hit()
        elif result.handled_by in {"guided_fallback", "legacy_chat"}:
            CoverageRecoveryMetricsService.record_miss()


def _is_recovery_hit(category: RecoveryCategory, result: HybridChatResult) -> bool:
    query_type = result.metadata.get("query_type")
    if category == RecoveryCategory.CAPABILITY_DISCOVERY:
        return result.handled_by == "capability_discovery"
    if category == RecoveryCategory.DATA_COVERAGE:
        return (
            result.handled_by == "business_pipeline"
            and query_type == RecoveryCategory.DATA_COVERAGE.value
        )
    if category == RecoveryCategory.DATASET_INFO:
        return (
            result.handled_by == "business_pipeline"
            and query_type == RecoveryCategory.DATASET_INFO.value
        )
    return False
