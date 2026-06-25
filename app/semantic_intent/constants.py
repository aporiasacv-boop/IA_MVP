SBEP_VERSION = "1.0.0"
SBEP_SCHEMA_ID = "business_execution_plan_v1"

VERB_CATEGORIES = (
    "informative",
    "analytic",
    "executive",
    "conversational",
    "future",
)

EXECUTION_STRATEGIES = (
    "eko_identity_lookup",
    "eko_profile_summary",
    "eko_full_analysis",
    "ero_risk_assessment",
    "ero_recommendation_review",
    "eko_ero_combined",
    "ontology_exploration",
    "capability_discovery",
    "unknown",
)

EKO_SECTIONS = (
    "identity",
    "roles",
    "nature",
    "behaviors",
    "facts",
    "signals",
    "alerts",
    "patterns",
    "relationships",
    "quality",
    "evidence",
)

ERO_SECTIONS = (
    "findings",
    "signals",
    "alerts",
    "risks",
    "opportunities",
    "recommendations",
    "evidence",
)

TIME_PATTERNS = (
    "este mes",
    "mes pasado",
    "este año",
    "año pasado",
    "último trimestre",
    "ultimo trimestre",
    "trimestre",
    "hoy",
    "ayer",
)

SCOPE_PATTERNS = (
    "top",
    "principales",
    "mayor",
    "menor",
    "todos",
    "todas",
    "principal",
    "mejor",
    "peor",
)
