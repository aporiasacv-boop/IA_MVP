from pathlib import Path

ERO_VERSION = "1.0.0"
ERO_SCHEMA_ID = "enterprise_reasoning_object_v1"

RULES_DIR = Path(__file__).resolve().parent / "rules"

CONCLUSION_TYPES = (
    "finding",
    "signal",
    "alert",
    "risk",
    "opportunity",
    "recommendation",
)

SEVERITY_LEVELS = ("low", "medium", "high", "critical")

REQUIRED_SECTIONS = (
    "findings",
    "signals",
    "alerts",
    "risks",
    "opportunities",
    "recommendations",
    "evidence",
    "confidence",
    "metadata",
)

SORTABLE_REASONING_FIELDS = ("average_confidence", "built_at", "findings_count", "canonical_name")
