PROFILE_ENTERPRISE_INTELLIGENCE_DIRECTOR = "enterprise_intelligence_director"

ADAPTATION_INSTITUTIONAL_INTRO = "institutional_intro"
ADAPTATION_DIRECT_ENGAGEMENT = "direct_engagement"
ADAPTATION_CONSULTANT_MODE = "consultant_mode"
ADAPTATION_GUIDED_RECOVERY = "guided_recovery"
ADAPTATION_EXPLORATION = "exploration"
ADAPTATION_CLOSURE = "closure"

FORBIDDEN_PHRASES: tuple[str, ...] = (
    "soy un modelo de ia",
    "como inteligencia artificial",
    "como ia",
    "no tengo emociones",
    "soy un chatbot",
    "soy un bot",
    "openai",
    "chatgpt",
    "ollama",
    "lenguaje natural processing",
)

PROTECTED_HANDLED_BY = frozenset({
    "business_pipeline",
    "slot_clarification",
    "conversation_memory",
    "executive_reasoning",
})
