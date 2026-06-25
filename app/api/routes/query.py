from fastapi import APIRouter, Depends, Query

from app.api.deps import get_business_query_executor, get_business_query_response_engine
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_planner import BusinessQueryPlanner
from app.query_executor.business_query_executor import BusinessQueryExecutor
from app.query_executor.query_result import BusinessQueryResult
from app.response_engine.deterministic_response_engine import DeterministicResponseEngine
from app.response_engine.response_result import BusinessResponse
from app.services.semantic_intent_builder import SemanticIntentBuilder

router = APIRouter(prefix="/api/query", tags=["query"])

_semantic_intent_builder = SemanticIntentBuilder()
_query_planner = BusinessQueryPlanner()


@router.get(
    "/plan",
    response_model=BusinessQuery,
    summary="Planificar consulta empresarial deterministica",
    description=(
        "Convierte una pregunta en lenguaje natural en un plan de consulta tipado. "
        "Flujo: SemanticIntentBuilder -> BusinessQueryPlanner. "
        "No ejecuta SQL ni accede a PostgreSQL."
    ),
)
def plan_query(
    question: str = Query(
        ...,
        min_length=1,
        description="Pregunta empresarial en lenguaje natural",
        examples=["¿Cuántos clientes existen?"],
    ),
) -> BusinessQuery:
    intent = _semantic_intent_builder.build(question)
    return _query_planner.plan(intent)


@router.get(
    "/execute",
    response_model=BusinessQueryResult,
    summary="Ejecutar consulta empresarial deterministica",
    description=(
        "Convierte una pregunta en lenguaje natural en un resultado estructurado "
        "del Data Mart. Flujo: SemanticIntentBuilder -> BusinessQueryPlanner -> "
        "BusinessQueryExecutor."
    ),
)
def execute_query(
    question: str = Query(
        ...,
        min_length=1,
        description="Pregunta empresarial en lenguaje natural",
        examples=["¿Cuántos clientes existen?"],
    ),
    executor: BusinessQueryExecutor = Depends(get_business_query_executor),
) -> BusinessQueryResult:
    intent = _semantic_intent_builder.build(question)
    query = _query_planner.plan(intent)
    return executor.execute(query)


@router.get(
    "/respond",
    response_model=BusinessResponse,
    summary="Responder consulta empresarial deterministica",
    description=(
        "Pipeline completo: pregunta -> intent -> query -> executor -> respuesta legible. "
        "No utiliza LLM ni IA generativa."
    ),
)
def respond_query(
    question: str = Query(
        ...,
        min_length=1,
        description="Pregunta empresarial en lenguaje natural",
        examples=["¿Cuántos clientes existen?"],
    ),
    executor: BusinessQueryExecutor = Depends(get_business_query_executor),
    response_engine: DeterministicResponseEngine = Depends(get_business_query_response_engine),
) -> BusinessResponse:
    intent = _semantic_intent_builder.build(question)
    query = _query_planner.plan(intent)
    query_result = executor.execute(query)
    return response_engine.generate(query_result)
