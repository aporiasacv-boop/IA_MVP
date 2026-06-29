from enum import Enum
import re
import unicodedata

from app.utils.text_normalizer import normalize_for_matching


class ConversationCategory(str, Enum):
    GREETING = "greeting"
    FAREWELL = "farewell"
    CASUAL = "casual"
    SOCIAL = "social"
    IDENTITY = "identity"
    CAPABILITIES = "capabilities"
    EXECUTIVE_GENERAL = "executive_general"
    HELP = "help"
    INTRODUCTION = "introduction"
    NONE = "none"


CONVERSATIONAL_CATEGORIES = frozenset({
    ConversationCategory.GREETING,
    ConversationCategory.FAREWELL,
    ConversationCategory.CASUAL,
    ConversationCategory.SOCIAL,
    ConversationCategory.IDENTITY,
    ConversationCategory.CAPABILITIES,
    ConversationCategory.EXECUTIVE_GENERAL,
    ConversationCategory.HELP,
    ConversationCategory.INTRODUCTION,
})


_GREETING_PATTERNS: tuple[str, ...] = (
    r"^hola+$",
    r"^holaa+$",
    r"^ola+$",
    r"^hi$",
    r"^hello$",
    r"^buenos dias$",
    r"^buen dia$",
    r"^buenas tardes$",
    r"^buenas noches$",
    r"^saludos$",
)

_CASUAL_PATTERNS: tuple[str, ...] = (
    "como estas",
    "que tal",
    "que onda",
    "como va",
    "como te va",
)

_IDENTITY_PATTERNS: tuple[str, ...] = (
    "quien eres",
    "que eres",
    "como te llamas",
    "cual es tu nombre",
    "eres una ia",
    "eres una inteligencia artificial",
    "quien te creo",
    "quien te desarrollo",
)

_CAPABILITIES_PATTERNS: tuple[str, ...] = (
    "que puedes hacer",
    "que sabes hacer",
    "que puedo preguntarte",
    "que consultas soportas",
    "que consultas puedes",
    "que consultas puedo",
    "como puedes ayudarme",
    "para que sirves",
    "capacidades del sistema",
    "cuales son tus capacidades",
    "que haces",
    "como me ayudas",
)

_EXECUTIVE_PATTERNS: tuple[str, ...] = (
    "como ves el negocio",
    "como va el negocio",
    "que informacion tienes",
    "que informacion manejas",
    "que datos tienes disponibles",
    "que puedes analizar",
    "que puedes analizar hoy",
    "por donde empezamos",
    "por donde podemos empezar",
    "que me recomiendas preguntar",
    "que deberia preguntar",
    "que deberia analizar",
    "dame un panorama",
    "panorama del negocio",
    "resumen ejecutivo",
    "como empezamos",
)

_HELP_PATTERNS: tuple[str, ...] = (
    "ayuda",
    "necesito ayuda",
    "no entiendo",
    "como funciona",
    "como te uso",
    "como usar el asistente",
)

_FAREWELL_PATTERNS: tuple[str, ...] = (
    "adios",
    "hasta luego",
    "hasta pronto",
    "nos vemos",
    "chao",
    "bye",
    "goodbye",
    "me voy",
    "hasta manana",
)

_INTRODUCTION_PATTERNS: tuple[str, ...] = (
    "presentate",
    "presentate por favor",
    "que es olnatura intelligence",
    "quien es olnatura intelligence",
    "cuentame de ti",
    "cuentame sobre ti",
)

_SOCIAL_PATTERNS: tuple[str, ...] = (
    "gracias",
    "muchas gracias",
    "excelente trabajo",
    "muy bien",
    "genial",
    "perfecto",
    "buen trabajo",
    "te lo agradezco",
    "estupendo",
)


def _normalize_question(text: str) -> str:
    lowered = text.lower().strip()
    decomposed = unicodedata.normalize("NFD", lowered)
    without_accents = "".join(
        char for char in decomposed if unicodedata.category(char) != "Mn"
    )
    cleaned = re.sub(r"[^\w\s]", " ", without_accents)
    return re.sub(r"\s+", " ", cleaned).strip()


def _matches_any(normalized: str, patterns: tuple[str, ...]) -> bool:
    return any(
        normalized == pattern or normalized.startswith(f"{pattern} ")
        for pattern in patterns
    )


def _matches_greeting(normalized: str) -> bool:
    return any(re.match(pattern, normalized) for pattern in _GREETING_PATTERNS)


def is_conversational(category: ConversationCategory) -> bool:
    return category in CONVERSATIONAL_CATEGORIES


def classify_message(message: str) -> ConversationCategory:
    normalized = _normalize_question(message)
    if not normalized:
        return ConversationCategory.NONE

    if _matches_greeting(normalized):
        return ConversationCategory.GREETING
    if _matches_any(normalized, _FAREWELL_PATTERNS):
        return ConversationCategory.FAREWELL
    if _matches_any(normalized, _INTRODUCTION_PATTERNS):
        return ConversationCategory.INTRODUCTION
    if _matches_any(normalized, _IDENTITY_PATTERNS):
        return ConversationCategory.IDENTITY
    if _matches_any(normalized, _CAPABILITIES_PATTERNS):
        return ConversationCategory.CAPABILITIES
    if _matches_any(normalized, _EXECUTIVE_PATTERNS):
        return ConversationCategory.EXECUTIVE_GENERAL
    if _matches_any(normalized, _CASUAL_PATTERNS):
        return ConversationCategory.CASUAL
    if _matches_any(normalized, _SOCIAL_PATTERNS):
        return ConversationCategory.SOCIAL
    if _matches_any(normalized, _HELP_PATTERNS):
        return ConversationCategory.HELP

    compact = normalize_for_matching(message)
    if compact in {"hola", "buenos dias", "buenas tardes", "buenas noches", "saludos"}:
        return ConversationCategory.GREETING
    if compact in {"adios", "hasta luego", "gracias", "muchas gracias"}:
        if compact in {"adios", "hasta luego"}:
            return ConversationCategory.FAREWELL
        return ConversationCategory.SOCIAL

    return ConversationCategory.NONE


def greeting_time_phrase(message: str) -> str:
    normalized = _normalize_question(message)
    if "buenos dias" in normalized or "buen dia" in normalized:
        return "Buenos días"
    if "buenas tardes" in normalized:
        return "Buenas tardes"
    if "buenas noches" in normalized:
        return "Buenas noches"
    return "Hola"
