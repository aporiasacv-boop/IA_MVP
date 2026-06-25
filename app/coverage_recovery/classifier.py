from enum import Enum

from app.coverage_recovery.patterns import (
    CAPABILITY_DISCOVERY_PATTERNS,
    DATA_COVERAGE_PATTERNS,
    DATASET_INFO_PATTERNS,
)
from app.utils.text_normalizer import normalize_for_matching


class RecoveryCategory(str, Enum):
    DATA_COVERAGE = "DATA_COVERAGE"
    DATASET_INFO = "DATASET_INFO"
    CAPABILITY_DISCOVERY = "CAPABILITY_DISCOVERY"


def classify_recovery_question(question: str) -> RecoveryCategory | None:
    """Clasifica si una pregunta pertenece a un bucket de recuperación de cobertura."""
    normalized = normalize_for_matching(question)
    if not normalized:
        return None

    if _matches_any(normalized, DATASET_INFO_PATTERNS):
        return RecoveryCategory.DATASET_INFO
    if _matches_any(normalized, DATA_COVERAGE_PATTERNS):
        return RecoveryCategory.DATA_COVERAGE
    if _matches_any(normalized, CAPABILITY_DISCOVERY_PATTERNS):
        return RecoveryCategory.CAPABILITY_DISCOVERY
    return None


def _matches_any(normalized: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in normalized for pattern in patterns)
