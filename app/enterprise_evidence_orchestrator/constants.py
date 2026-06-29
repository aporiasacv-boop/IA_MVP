MIN_PACKAGE_COVERAGE = 60.0
MIN_EVIDENCE_ITEMS = 1

SOURCE_BUSINESS_PIPELINE = "business_pipeline"

ORCHESTRATOR_SKIP_QUESTION_PATTERNS: tuple[str, ...] = (
    "sentido de la vida",
    "significado de la vida",
)

SKIP_FALLBACK_TYPES: frozenset[str] = frozenset({"OUT_OF_DOMAIN"})
