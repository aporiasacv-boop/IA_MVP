from app.enterprise_decision.repository import DecisionContext
from app.enterprise_decision.schemas import DecisionHealthResponse

EXPECTED_SOURCES = {
    "enterprise_knowledge_service",
    "eko",
    "ero",
    "eep",
    "operational_metrics",
    "finops",
    "simulation_engine",
}


def build_decision_health(context: DecisionContext) -> DecisionHealthResponse:
    available = sorted(set(context.sources_used))
    missing = sorted(EXPECTED_SOURCES - set(available))
    status = "healthy" if len(available) >= 3 else "degraded" if available else "unavailable"
    return DecisionHealthResponse(
        status=status,
        available_sources=available,
        missing_sources=missing,
    )
