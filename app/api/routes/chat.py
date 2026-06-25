import time



from fastapi import APIRouter, Depends



from app.api.deps import (

    get_business_context_builder,

    get_deterministic_response_engine,

    get_query_executor,

    get_response_generator,

)

from app.schemas.chat import ChatRequest, ChatResponse

from app.schemas.prompt_metrics import PromptMetrics

from app.schemas.response_mode import ResponseMode

from app.services.business_context_builder import BusinessContextBuilder

from app.services.deterministic_response_engine import DeterministicResponseEngine

from app.services.entity_extraction_layer import EntityExtractionLayer

from app.services.human_language_layer import HumanLanguageLayer

from app.services.intent_router import IntentRouter

from app.services.query_executor import QueryExecutor

from app.services.response_generator import ResponseGenerator

from app.services.response_mode_resolver import ResponseModeResolver

from app.services.social_identity_layer import SocialIdentityLayer

from app.services.executive_capability_layer import ExecutiveCapabilityLayer

from app.services.system_explanation_layer import SystemExplanationLayer

from app.services.timing_collector import TimingCollector, elapsed_ms

from app.services.token_optimization_layer import TokenOptimizationLayer



router = APIRouter(prefix="/api", tags=["chat"])

intent_router = IntentRouter()

human_language_layer = HumanLanguageLayer()

entity_extraction_layer = EntityExtractionLayer()

token_optimization_layer = TokenOptimizationLayer()

system_explanation_layer = SystemExplanationLayer()

executive_capability_layer = ExecutiveCapabilityLayer()

social_identity_layer = SocialIdentityLayer()

response_mode_resolver = ResponseModeResolver()





@router.post(

    "/chat",

    response_model=ChatResponse,

    summary="Chat empresarial con narrativa ejecutiva",

    description=(

        "Clasifica la pregunta, construye contexto simple o consolidado y genera "

        "respuesta en lenguaje natural con Ollama sobre datos verificados."

    ),

)

def chat(

    request: ChatRequest,

    executor: QueryExecutor = Depends(get_query_executor),

    context_builder: BusinessContextBuilder = Depends(get_business_context_builder),

    response_generator: ResponseGenerator = Depends(get_response_generator),

    deterministic_engine: DeterministicResponseEngine = Depends(get_deterministic_response_engine),

) -> ChatResponse:

    timings = TimingCollector()



    hl_result = human_language_layer.process(request.question, timings=timings)



    entities = entity_extraction_layer.extract(

        hl_result.normalized_question,

        alternate_text=hl_result.original_question,

        timings=timings,

    )



    token_match = token_optimization_layer.process(

        hl_result.original_question,

        alternate_text=hl_result.normalized_question,

        timings=timings,

    )

    if token_match is not None:

        timings.mark_total()

        return ChatResponse(

            intent=token_match.intent.value,

            intent_confidence=token_match.confidence,

            response_mode=ResponseMode.DETERMINISTIC,

            answer=token_match.answer,

            data={"layer": "token_optimization"},

            original_question=hl_result.original_question,

            normalized_question=hl_result.normalized_question,

            corrections_applied=hl_result.corrections_applied,

            entities=entities,

            sources=[],

            timings=timings.to_model(),

            prompt_metrics=PromptMetrics(),

            token_optimization_demo=token_match.demo,

        )



    explanation_match = system_explanation_layer.process(

        hl_result.original_question,

        alternate_text=hl_result.normalized_question,

        timings=timings,

    )

    if explanation_match is not None:

        timings.mark_total()

        return ChatResponse(

            intent=explanation_match.intent.value,

            intent_confidence=explanation_match.confidence,

            response_mode=ResponseMode.DETERMINISTIC,

            answer=explanation_match.answer,

            data={

                "layer": "system_explanation",

                "match_type": explanation_match.match_type,

            },

            original_question=hl_result.original_question,

            normalized_question=hl_result.normalized_question,

            corrections_applied=hl_result.corrections_applied,

            entities=entities,

            sources=[],

            timings=timings.to_model(),

            prompt_metrics=PromptMetrics(),

        )



    capability_match = executive_capability_layer.process(

        hl_result.original_question,

        alternate_text=hl_result.normalized_question,

        timings=timings,

    )

    if capability_match is not None:

        timings.mark_total()

        return ChatResponse(

            intent=capability_match.intent.value,

            intent_confidence=capability_match.confidence,

            response_mode=ResponseMode.DETERMINISTIC,

            answer=capability_match.answer,

            data={

                "layer": "executive_capability",

                "match_type": capability_match.match_type,

            },

            original_question=hl_result.original_question,

            normalized_question=hl_result.normalized_question,

            corrections_applied=hl_result.corrections_applied,

            entities=entities,

            sources=[],

            timings=timings.to_model(),

            prompt_metrics=PromptMetrics(),

        )



    social_match = social_identity_layer.process(

        hl_result.original_question,

        alternate_text=hl_result.normalized_question,

        timings=timings,

    )



    if social_match is not None:

        timings.mark_total()

        return ChatResponse(

            intent=social_match.intent.value,

            intent_confidence=social_match.confidence,

            response_mode=ResponseMode.DETERMINISTIC,

            answer=social_match.answer,

            data={"layer": "social_identity"},

            original_question=hl_result.original_question,

            normalized_question=hl_result.normalized_question,

            corrections_applied=hl_result.corrections_applied,

            entities=entities,

            sources=[],

            timings=timings.to_model(),

            prompt_metrics=PromptMetrics(),

        )



    router_started = time.perf_counter()

    match = intent_router.route(

        hl_result.normalized_question,

        corrections_applied=hl_result.corrections_applied,

        intent_hint=hl_result.intent_hint,

    )

    timings.router_ms = elapsed_ms(router_started)



    response_mode = response_mode_resolver.resolve(match.intent)

    question_for_context = hl_result.normalized_question

    low_confidence = match.confidence < 0.60



    if response_mode == ResponseMode.DETERMINISTIC and not low_confidence:

        deterministic_result = deterministic_engine.generate(match, entities, timings=timings)

        timings.mark_total()

        return ChatResponse(

            intent=match.intent.value,

            intent_confidence=match.confidence,

            response_mode=ResponseMode.DETERMINISTIC,

            answer=deterministic_result.answer,

            data=deterministic_result.data,

            original_question=hl_result.original_question,

            normalized_question=hl_result.normalized_question,

            corrections_applied=hl_result.corrections_applied,

            entities=entities,

            sources=deterministic_result.sources,

            timings=timings.to_model(),

            prompt_metrics=PromptMetrics(),

        )



    sources: list[str] = []



    if low_confidence or match.intent.value == "UNKNOWN":

        data = None

    elif context_builder.is_executive(match.intent):

        executive_context = context_builder.build(

            match.intent,

            question_for_context,

            timings=timings,

        )

        data = executive_context.data

        sources = executive_context.sources

    else:

        data = executor.execute(match, timings=timings)



    answer, prompt_metrics = response_generator.generate(

        question_for_context,

        match.intent.value,

        data,

        intent_confidence=match.confidence,

        sources=sources,

        timings=timings,

    )

    timings.mark_total()



    return ChatResponse(

        intent=match.intent.value,

        intent_confidence=match.confidence,

        response_mode=ResponseMode.GENERATIVE,

        answer=answer,

        data=data,

        original_question=hl_result.original_question,

        normalized_question=hl_result.normalized_question,

        corrections_applied=hl_result.corrections_applied,

        entities=entities,

        sources=sources,

        timings=timings.to_model(),

        prompt_metrics=prompt_metrics,

    )


