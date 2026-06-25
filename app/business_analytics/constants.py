DETERMINISTIC_ROUTES: frozenset[str] = frozenset({
    "business_pipeline",
    "slot_clarification",
    "conversation_memory",
    "capability_discovery",
    "guided_fallback",
})

AI_ROUTE = "legacy_chat"

ROUTE_FIELDS: tuple[str, ...] = (
    "business_pipeline",
    "slot_clarification",
    "conversation_memory",
    "capability_discovery",
    "guided_fallback",
    "legacy_chat",
)
