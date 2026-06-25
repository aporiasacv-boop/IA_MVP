from fastapi import APIRouter, Depends

from app.api.deps import get_hybrid_chat_router
from app.schemas.hybrid_chat import HybridChatRequest, HybridChatResult
from app.services.hybrid_chat_router import HybridChatRouter

router = APIRouter(prefix="/api", tags=["chat"])


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
    return hybrid_router.route(request.message, session_id=request.session_id)
