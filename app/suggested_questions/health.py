from app.query_engine.query_planner import BusinessQueryPlanner
from app.query_engine.query_types import BusinessQueryType
from app.services.semantic_intent_builder import SemanticIntentBuilder
from app.suggested_questions.engine import SuggestedQuestionsEngine
from app.suggested_questions.validator import is_registered_capability_question


class SuggestedQuestionsHealthError(Exception):
    pass


def validate_suggested_questions_health(
    engine: SuggestedQuestionsEngine | None = None,
) -> dict:
    engine = engine or SuggestedQuestionsEngine()
    planner = BusinessQueryPlanner()
    intent_builder = SemanticIntentBuilder()

    samples = [
        engine.generate(current_query_type=BusinessQueryType.COUNT_CLIENTES.value),
        engine.generate(current_query_type=BusinessQueryType.TOP_CLIENTES.value),
        engine.generate(current_query_type=BusinessQueryType.MAX_PROVEEDOR_MES.value),
        engine.generate(
            current_query_type="capability_discovery",
            handled_by="capability_discovery",
        ),
        engine.generate(
            current_query_type="UNKNOWN",
            handled_by="guided_fallback",
        ),
    ]

    for sample in samples:
        questions = sample.questions
        if len(questions) != len(set(q.strip().lower() for q in questions)):
            raise SuggestedQuestionsHealthError(
                "Las sugerencias deben ser únicas por respuesta."
            )
        if not questions:
            raise SuggestedQuestionsHealthError(
                f"Sin sugerencias para contexto {sample.metadata.get('query_type')}"
            )
        for question in questions:
            if not question.strip():
                raise SuggestedQuestionsHealthError("Sugerencia con texto vacío.")
            if not is_registered_capability_question(question):
                raise SuggestedQuestionsHealthError(
                    f"Sugerencia no corresponde a capacidad real: {question}"
                )
            intent = intent_builder.build(question)
            query = planner.plan(intent)
            if query.query_type == BusinessQueryType.UNSUPPORTED:
                raise SuggestedQuestionsHealthError(
                    f"El planner no soporta la sugerencia: {question}"
                )

    return {
        "samples_validated": len(samples),
        "min_questions": min(len(s.questions) for s in samples),
        "max_questions": max(len(s.questions) for s in samples),
    }
