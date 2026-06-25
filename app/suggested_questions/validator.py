from app.query_engine.query_catalog import QUERY_TYPE_EXAMPLE_QUESTIONS
from app.query_engine.query_planner import BusinessQueryPlanner
from app.query_engine.query_types import BusinessQueryType
from app.services.semantic_intent_builder import SemanticIntentBuilder

_planner = BusinessQueryPlanner()
_intent_builder = SemanticIntentBuilder()

KNOWN_QUESTIONS: set[str] = {
    question.lower()
    for question in QUERY_TYPE_EXAMPLE_QUESTIONS.values()
}


def is_planner_supported(question: str) -> bool:
    intent = _intent_builder.build(question)
    query = _planner.plan(intent)
    return query.query_type != BusinessQueryType.UNSUPPORTED


def is_registered_capability_question(question: str) -> bool:
    normalized = question.strip().lower()
    if normalized in KNOWN_QUESTIONS:
        return True
    return is_planner_supported(question)


def validate_questions(questions: list[str]) -> list[str]:
    validated: list[str] = []
    seen: set[str] = set()

    for question in questions:
        key = question.strip().lower()
        if not key or key in seen:
            continue
        if not is_planner_supported(question):
            continue
        validated.append(question)
        seen.add(key)

    return validated
