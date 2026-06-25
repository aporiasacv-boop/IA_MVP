from fastapi import APIRouter, Query

from app.schemas.entity import EntityResolution
from app.schemas.operation import OperationResolution
from app.schemas.semantic_intent import BusinessSemanticIntent
from app.services.entity_resolver import EntityResolver
from app.services.operation_resolver import OperationResolver
from app.services.semantic_intent_builder import SemanticIntentBuilder

router = APIRouter(prefix="/api/semantic", tags=["semantic"])

_operation_resolver = OperationResolver()
_entity_resolver = EntityResolver()
_semantic_intent_builder = SemanticIntentBuilder()


@router.get(
    "/operation",
    response_model=OperationResolution,
    summary="Resolver operacion empresarial deterministica",
    description=(
        "Analiza una pregunta en lenguaje natural y detecta la operacion analitica "
        "subyacente usando un catalogo de sinonimos empresariales. "
        "No utiliza LLM ni embeddings."
    ),
)
def resolve_operation(
    question: str = Query(
        ...,
        min_length=1,
        description="Pregunta empresarial en lenguaje natural",
        examples=["¿Cuántos clientes existen?"],
    ),
) -> OperationResolution:
    return _operation_resolver.resolve(question)


@router.get(
    "/entity",
    response_model=EntityResolution,
    summary="Resolver entidades empresariales deterministica",
    description=(
        "Analiza una pregunta en lenguaje natural y detecta entidades de negocio "
        "y parametros asociados usando un catalogo de sinonimos empresariales. "
        "No utiliza LLM ni embeddings."
    ),
)
def resolve_entity(
    question: str = Query(
        ...,
        min_length=1,
        description="Pregunta empresarial en lenguaje natural",
        examples=["¿De qué cliente es la cuenta IMA0709183?"],
    ),
) -> EntityResolution:
    return _entity_resolver.resolve(question)


@router.get(
    "/intent",
    response_model=BusinessSemanticIntent,
    summary="Construir intent semantico empresarial determinista",
    description=(
        "Unifica Operation Resolver y Entity Resolver para producir un contrato "
        "semantico tipado listo para el futuro Business Query Engine. "
        "No utiliza LLM ni embeddings."
    ),
)
def build_semantic_intent(
    question: str = Query(
        ...,
        min_length=1,
        description="Pregunta empresarial en lenguaje natural",
        examples=["¿Cuál fue la transacción más alta del cliente C001?"],
    ),
) -> BusinessSemanticIntent:
    return _semantic_intent_builder.build(question)
