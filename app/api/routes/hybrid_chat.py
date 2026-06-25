import time

from fastapi import APIRouter, Depends

from app.api.deps import get_hybrid_chat_router
from app.enterprise_knowledge_service.integration.consumers import knowledge_for_chat
from app.operational_metrics.service import record_hybrid_operational_query
from app.schemas.hybrid_chat import HybridChatRequest, HybridChatResult
from app.services.hybrid_chat_router import HybridChatRouter

router = APIRouter(prefix="/api", tags=["chat"])


def _with_response_time(result: HybridChatResult, elapsed_ms: float) -> HybridChatResult:
    return HybridChatResult(
        handled_by=result.handled_by,
        success=result.success,
        answer=result.answer,
        suggestions=result.suggestions,
        metadata={**result.metadata, "response_time_ms": round(elapsed_ms, 2)},
    )


@router.post(
    "/chat/hybrid",
    response_model=HybridChatResult,
    summary="Chat hibrido experimental",
    description=(
        "Enruta la pregunta al pipeline empresarial determinista o al chat legacy "
        "segun el query_type planificado. No reemplaza /api/chat."
    ),
)
def hybrid_chat(
    request: HybridChatRequest,
    hybrid_router: HybridChatRouter = Depends(get_hybrid_chat_router),
) -> HybridChatResult:
    started = time.perf_counter()
    identity_result, knowledge_result = knowledge_for_chat(request.message)
    if identity_result is not None:
        result = _with_response_time(identity_result, (time.perf_counter() - started) * 1000)
        record_hybrid_operational_query(request, result, result.metadata.get("response_time_ms", 0.0))
        return result
    if knowledge_result is not None:
        result = _with_response_time(knowledge_result, (time.perf_counter() - started) * 1000)
        record_hybrid_operational_query(request, result, result.metadata.get("response_time_ms", 0.0))
        return result
    result = hybrid_router.route(request.message, session_id=request.session_id)
    result = _with_response_time(result, (time.perf_counter() - started) * 1000)
    record_hybrid_operational_query(request, result, result.metadata.get("response_time_ms", 0.0))
    return result
