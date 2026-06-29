import time
from collections.abc import Callable
from dataclasses import dataclass

from app.ai_orchestration.service import AIOrchestrationService, is_executive_reasoning_candidate
from app.core.settings import settings
from app.observability.performance_metrics import elapsed_ms
from app.schemas.hybrid_chat import HybridChatResult

ExecutiveReasoningHandler = Callable[[str], HybridChatResult]


@dataclass(frozen=True)
class ExecutiveReasoningStage:
    """Resultado de razonamiento ejecutivo con tiempo de etapa para el pipeline."""

    result: HybridChatResult
    stage_ms: float


class ExecutiveReasoningCapability:
    """Ejecuta razonamiento ejecutivo para consultas no soportadas por el pipeline determinístico."""

    def __init__(self, handler: ExecutiveReasoningHandler | None = None) -> None:
        self._handler = handler

    @classmethod
    def from_orchestration_service(
        cls,
        orchestration_service: AIOrchestrationService,
    ) -> "ExecutiveReasoningCapability":
        from app.ai_orchestration.schemas import ExecutiveGenerateRequest

        def handler(message: str) -> HybridChatResult:
            response = orchestration_service.generate(
                ExecutiveGenerateRequest(question=message),
            )
            answer = orchestration_service.format_executive_answer(response)
            evidence_sources = [
                f"{citation.source}:{citation.key}" for citation in response.citations[:5]
            ]
            return HybridChatResult(
                handled_by="executive_reasoning",
                success=not response.hallucination_guard_triggered or bool(answer),
                answer=answer,
                metadata={
                    "handled_by": "executive_reasoning",
                    "provider": response.provider,
                    "model": response.model,
                    "confidence": float(response.confidence),
                    "tokens_input": response.tokens_input,
                    "tokens_output": response.tokens_output,
                    "estimated_cost": response.estimated_cost,
                    "hallucination_guard_triggered": response.hallucination_guard_triggered,
                    "evidence_package_id": response.evidence_package_id,
                    "limitations": response.limitations,
                    "evidence_sources": evidence_sources,
                    "response_time_ms": round(response.response_time * 1000, 2),
                },
            )

        return cls(handler=handler)

    def try_reason(self, message: str) -> ExecutiveReasoningStage | None:
        if not settings.EXECUTIVE_REASONING_ENABLED:
            return None
        if self._handler is None:
            return None
        if not is_executive_reasoning_candidate(message):
            return None

        started = time.perf_counter()
        result = self._handler(message)
        return ExecutiveReasoningStage(result=result, stage_ms=elapsed_ms(started))
