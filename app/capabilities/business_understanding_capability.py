import time
from dataclasses import dataclass

from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_planner import BusinessQueryPlanner
from app.observability.performance_metrics import elapsed_ms
from app.schemas.semantic_intent import BusinessSemanticIntent
from app.services.semantic_intent_builder import SemanticIntentBuilder


@dataclass(frozen=True)
class BusinessUnderstandingResult:
    """Consulta estructurada derivada de la comprensión semántica del mensaje."""

    intent: BusinessSemanticIntent
    query: BusinessQuery


@dataclass(frozen=True)
class BusinessUnderstandingStage:
    """Resultado de comprensión con tiempos de etapa para el pipeline."""

    result: BusinessUnderstandingResult
    intent_stage_ms: float
    planner_stage_ms: float


class BusinessUnderstandingCapability:
    """Núcleo de comprensión: intención semántica → planificación → consulta estructurada."""

    def __init__(
        self,
        intent_builder: SemanticIntentBuilder | None = None,
        query_planner: BusinessQueryPlanner | None = None,
    ) -> None:
        self._intent_builder = intent_builder or SemanticIntentBuilder()
        self._query_planner = query_planner or BusinessQueryPlanner()

    def understand(self, message: str) -> BusinessUnderstandingStage:
        intent_started = time.perf_counter()
        intent = self._intent_builder.build(message)
        intent_stage_ms = elapsed_ms(intent_started)

        planner_started = time.perf_counter()
        query = self._query_planner.plan(intent)
        planner_stage_ms = elapsed_ms(planner_started)

        return BusinessUnderstandingStage(
            result=BusinessUnderstandingResult(intent=intent, query=query),
            intent_stage_ms=intent_stage_ms,
            planner_stage_ms=planner_stage_ms,
        )
