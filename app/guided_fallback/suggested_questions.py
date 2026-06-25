from collections.abc import Callable

from app.query_engine.query_catalog import (
    DEFAULT_TOP_QUESTIONS,
    QUERY_TYPE_EXAMPLE_QUESTIONS,
)
from app.query_engine.query_types import BusinessQueryType

TopQuestionsProvider = Callable[[int], list[str]]

CAPABILITY_QUESTIONS: tuple[str, ...] = (
    "¿Cuántos clientes existen?",
    "¿Qué proveedor tuvo más movimiento en junio?",
    "¿Cuál es el periodo de los datos?",
    "¿Qué puedo preguntarte?",
    "Muéstrame los principales clientes",
)

def build_suggested_questions(
    *,
    top_questions_provider: TopQuestionsProvider,
    min_count: int = 3,
    max_count: int = 5,
) -> list[str]:
    suggestions: list[str] = []
    seen: set[str] = set()

    for question in top_questions_provider(max_count):
        key = question.strip().lower()
        if key and key not in seen:
            suggestions.append(question)
            seen.add(key)
        if len(suggestions) >= max_count:
            return suggestions[:max_count]

    for question in CAPABILITY_QUESTIONS:
        key = question.lower()
        if key not in seen:
            suggestions.append(question)
            seen.add(key)
        if len(suggestions) >= max_count:
            return suggestions[:max_count]

    for question in QUERY_TYPE_EXAMPLE_QUESTIONS.values():
        key = question.lower()
        if key not in seen:
            suggestions.append(question)
            seen.add(key)
        if len(suggestions) >= max_count:
            break

    while len(suggestions) < min_count:
        for question in DEFAULT_TOP_QUESTIONS:
            key = question.lower()
            if key not in seen:
                suggestions.append(question)
                seen.add(key)
            if len(suggestions) >= min_count:
                break
        break

    return suggestions[:max_count]
