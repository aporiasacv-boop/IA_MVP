from app.capability_discovery.engine import CapabilityDiscoveryEngine

from app.capability_discovery.v2.constants import V2_CAPABILITIES, V2_EXAMPLES

from app.capability_discovery.v2.validation import (

    CapabilityDiscoveryV2ValidationError,

    validate_v2_discovery_result,

)

from app.query_engine.query_planner import BusinessQueryPlanner

from app.query_engine.query_types import BusinessQueryType

from app.services.semantic_intent_builder import SemanticIntentBuilder





class CapabilityDiscoveryHealthError(Exception):

    pass





def validate_capability_discovery_health(

    engine: CapabilityDiscoveryEngine | None = None,

) -> dict:

    engine = engine or CapabilityDiscoveryEngine()

    result = engine.discover()



    try:

        validate_v2_discovery_result(

            answer=result.answer,

            capabilities=result.capabilities,

            example_questions=result.example_questions,

            suggestions_present=result.suggestions is not None

            and len(result.suggestions.questions) > 0,

        )

    except CapabilityDiscoveryV2ValidationError as exc:

        raise CapabilityDiscoveryHealthError(str(exc)) from exc



    if result.capabilities != list(V2_CAPABILITIES):

        raise CapabilityDiscoveryHealthError("Capacidades v2 no coinciden con el catálogo UX")



    if result.example_questions != list(V2_EXAMPLES):

        raise CapabilityDiscoveryHealthError("Ejemplos v2 no coinciden con el catálogo UX")



    planner = BusinessQueryPlanner()

    intent_builder = SemanticIntentBuilder()

    for question in result.example_questions:

        if not question or not question.strip():

            raise CapabilityDiscoveryHealthError(f"Pregunta ejemplo inválida: {question!r}")

        query = planner.plan(intent_builder.build(question))

        if query.query_type == BusinessQueryType.UNSUPPORTED:

            raise CapabilityDiscoveryHealthError(

                f"Ejemplo no ejecutable por el pipeline: {question}"

            )



    return {

        "capabilities_count": len(result.capabilities),

        "example_questions_count": len(result.example_questions),

        "discovery_version": result.metadata.get("discovery_version", "v2"),

        "capability_discovery_v2_responses": result.metadata.get(

            "capability_discovery_v2_responses",

            0,

        ),

        "capability_discovery_response_length": result.metadata.get(

            "capability_discovery_response_length",

            0,

        ),

    }


