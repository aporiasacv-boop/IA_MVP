import time
from dataclasses import dataclass

from app.query_engine.business_query import BusinessQuery
from app.query_executor.business_query_executor import BusinessQueryExecutor
from app.query_executor.query_result import BusinessQueryResult
from app.observability.performance_metrics import elapsed_ms
from app.response_engine.deterministic_response_engine import DeterministicResponseEngine
from app.response_engine.response_result import BusinessResponse


@dataclass(frozen=True)
class BusinessResolutionResult:
    """Evidencia estructurada y respuesta determinística de una consulta de negocio."""

    query_result: BusinessQueryResult
    response: BusinessResponse


@dataclass(frozen=True)
class BusinessResolutionStage:
    """Resultado de resolución con tiempos de etapa para el pipeline."""

    result: BusinessResolutionResult
    executor_stage_ms: float
    response_stage_ms: float


class BusinessResolutionCapability:
    """Ejecuta consultas de negocio y produce evidencia con respuesta determinística."""

    def __init__(
        self,
        query_executor: BusinessQueryExecutor,
        response_engine: DeterministicResponseEngine,
    ) -> None:
        self._query_executor = query_executor
        self._response_engine = response_engine

    def resolve(self, query: BusinessQuery) -> BusinessResolutionStage:
        executor_started = time.perf_counter()
        query_result = self._query_executor.execute(query)
        executor_stage_ms = elapsed_ms(executor_started)

        response_started = time.perf_counter()
        response = self._response_engine.generate(query_result)
        response_stage_ms = elapsed_ms(response_started)

        return BusinessResolutionStage(
            result=BusinessResolutionResult(
                query_result=query_result,
                response=response,
            ),
            executor_stage_ms=executor_stage_ms,
            response_stage_ms=response_stage_ms,
        )
