from collections.abc import Callable

from app.capability_discovery.registry import EXECUTABLE_QUERY_TYPES
from app.guided_fallback.suggested_questions import (
    DEFAULT_TOP_QUESTIONS,
    QUERY_TYPE_EXAMPLE_QUESTIONS,
)

TopQuestionsProvider = Callable[[int], list[str]]

ADDITIONAL_QUERY_EXAMPLES: dict[str, str] = {
    "TOP_PROVEEDORES": "¿Quién es el principal proveedor?",
}

PRIMARY_CAPABILITY_QUESTIONS: tuple[str, ...] = (
    "¿Cuántos clientes existen?",
    "¿Quién es el principal proveedor?",
    "¿Qué proveedor tuvo más movimiento en junio?",
    "¿Cuál es el periodo de los datos?",
    "Muéstrame los principales clientes",
)


def build_example_questions(
    *,
    top_questions_provider: TopQuestionsProvider,
    min_count: int = 5,
    max_count: int = 10,
) -> list[str]:
    examples: list[str] = []
    seen: set[str] = set()

    for question in top_questions_provider(max_count):
        key = question.strip().lower()
        if key and key not in seen:
            examples.append(question)
            seen.add(key)
        if len(examples) >= max_count:
            return examples[:max_count]

    for query_type in EXECUTABLE_QUERY_TYPES:
        question = QUERY_TYPE_EXAMPLE_QUESTIONS.get(query_type)
        if question:
            key = question.lower()
            if key not in seen:
                examples.append(question)
                seen.add(key)
        extra = ADDITIONAL_QUERY_EXAMPLES.get(query_type.value)
        if extra:
            key = extra.lower()
            if key not in seen:
                examples.append(extra)
                seen.add(key)
        if len(examples) >= max_count:
            return examples[:max_count]

    for question in PRIMARY_CAPABILITY_QUESTIONS:
        key = question.lower()
        if key not in seen:
            examples.append(question)
            seen.add(key)
        if len(examples) >= max_count:
            return examples[:max_count]

    for question in DEFAULT_TOP_QUESTIONS:
        key = question.lower()
        if key not in seen:
            examples.append(question)
            seen.add(key)
        if len(examples) >= max_count:
            break

    while len(examples) < min_count:
        for question in DEFAULT_TOP_QUESTIONS:
            key = question.lower()
            if key not in seen:
                examples.append(question)
                seen.add(key)
            if len(examples) >= min_count:
                break
        break

    return examples[:max_count]
