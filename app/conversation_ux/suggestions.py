from app.conversation_ux.classifier import ConversationCategory
from app.conversation_ux.context import DatasetSnapshot
from app.query_engine.query_catalog import DEFAULT_TOP_QUESTIONS


_EXECUTIVE_STARTERS: tuple[str, ...] = (
    "¿Qué pasó en junio?",
    "¿Quién es nuestro mejor cliente?",
    "¿Qué proveedor tuvo más movimiento en junio?",
    "¿Cuál fue el mes con mayor actividad?",
    "¿Qué riesgos de concentración detectas en clientes?",
)

_CAPABILITY_STARTERS: tuple[str, ...] = (
    "¿Cuántos clientes existen?",
    "¿Cuántos proveedores existen?",
    "Muéstrame los principales clientes",
    "¿Qué proveedor tuvo más movimiento en junio?",
    "¿Cuál es el periodo de los datos?",
)

_IDENTITY_STARTERS: tuple[str, ...] = (
    "¿Qué puedes hacer?",
    "¿Qué pasó en junio?",
    "¿Quién es nuestro mejor cliente?",
    "¿Cuál es el periodo de los datos?",
)

_GREETING_STARTERS: tuple[str, ...] = (
    "¿Qué puedes hacer?",
    "¿Qué pasó en junio?",
    "¿Quién es nuestro mejor cliente?",
    "¿Cuál es el periodo de los datos?",
    "¿Qué proveedor tuvo más movimiento en junio?",
)

_HELP_STARTERS: tuple[str, ...] = (
    "¿Qué puedes hacer?",
    "¿Cuántos clientes existen?",
    "¿Qué pasó en junio?",
    "Muéstrame los principales clientes",
)


def build_conversational_suggestions(
    category: ConversationCategory,
    *,
    capability_examples: list[str] | None = None,
    min_count: int = 3,
    max_count: int = 5,
) -> list[str]:
    pools: list[str] = []
    if category == ConversationCategory.CAPABILITIES:
        pools.extend(capability_examples or [])
        pools.extend(_CAPABILITY_STARTERS)
    elif category == ConversationCategory.EXECUTIVE_GENERAL:
        pools.extend(_EXECUTIVE_STARTERS)
        pools.extend(DEFAULT_TOP_QUESTIONS)
    elif category == ConversationCategory.IDENTITY:
        pools.extend(_IDENTITY_STARTERS)
    elif category == ConversationCategory.HELP:
        pools.extend(_HELP_STARTERS)
    elif category in {
        ConversationCategory.FAREWELL,
        ConversationCategory.SOCIAL,
        ConversationCategory.INTRODUCTION,
    }:
        pools.extend(_GREETING_STARTERS)
    else:
        pools.extend(_GREETING_STARTERS)

    suggestions: list[str] = []
    seen: set[str] = set()
    for question in pools:
        key = question.strip().lower()
        if not key or key in seen:
            continue
        suggestions.append(question)
        seen.add(key)
        if len(suggestions) >= max_count:
            break

    for question in DEFAULT_TOP_QUESTIONS:
        if len(suggestions) >= min_count:
            break
        key = question.lower()
        if key not in seen:
            suggestions.append(question)
            seen.add(key)

    return suggestions[:max_count]
