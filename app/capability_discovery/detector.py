from app.utils.text_normalizer import normalize_for_matching

CAPABILITY_DISCOVERY_PATTERNS: tuple[str, ...] = (
    "que puedes hacer",
    "que sabes hacer",
    "que puedo preguntarte",
    "que consultas soportas",
    "que consultas puedes",
    "que consultas puedo",
    "como puedes ayudarme",
    "para que sirves",
    "capacidades del sistema",
    "capacidades",
    "funciones",
)


def is_capability_discovery(question: str) -> bool:
    normalized = normalize_for_matching(question)
    return any(pattern in normalized for pattern in CAPABILITY_DISCOVERY_PATTERNS)
