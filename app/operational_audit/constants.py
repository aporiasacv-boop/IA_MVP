GAP_ROUTES: frozenset[str] = frozenset({"legacy_chat", "guided_fallback"})

ROUTE_ALIASES: dict[str, str] = {
    "business_pipeline": "business_pipeline",
    "slot_clarification": "slot_clarification",
    "conversation_memory": "conversation_memory",
    "capability_discovery": "capability_discovery",
    "guided_fallback": "guided_fallback",
    "legacy_chat": "legacy_chat",
}

OVERVIEW_PCT_FIELDS: tuple[str, ...] = (
    "business_pipeline_pct",
    "memory_pct",
    "clarification_pct",
    "capability_pct",
    "fallback_pct",
    "legacy_pct",
)
