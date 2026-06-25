from fastapi import APIRouter, Depends

from app.ai_orchestration.schemas import (
    AICostSummaryResponse,
    ExecutiveGenerateFromPackageRequest,
    ExecutiveGenerateRequest,
    ExecutiveResponse,
    ExecutiveSchemaResponse,
    OrchestrationHealthResponse,
    OrchestrationStatisticsResponse,
)
from app.ai_orchestration.service import AIOrchestrationService
from app.api.deps import get_ai_orchestration_service

router = APIRouter(prefix="/api/executive-response", tags=["executive-response"])


@router.post("/generate", response_model=ExecutiveResponse)
def generate_executive_response(
    request: ExecutiveGenerateRequest,
    service: AIOrchestrationService = Depends(get_ai_orchestration_service),
) -> ExecutiveResponse:
    return service.generate(request)


@router.post("/generate-from-package", response_model=ExecutiveResponse)
def generate_from_package(
    request: ExecutiveGenerateFromPackageRequest,
    service: AIOrchestrationService = Depends(get_ai_orchestration_service),
) -> ExecutiveResponse:
    return service.generate_from_package(request.evidence_package)


@router.get("/schema", response_model=ExecutiveSchemaResponse)
def get_executive_schema(
    service: AIOrchestrationService = Depends(get_ai_orchestration_service),
) -> ExecutiveSchemaResponse:
    return service.get_schema()


@router.get("/statistics", response_model=OrchestrationStatisticsResponse)
def get_executive_statistics(
    service: AIOrchestrationService = Depends(get_ai_orchestration_service),
) -> OrchestrationStatisticsResponse:
    return service.get_statistics()


@router.get("/health", response_model=OrchestrationHealthResponse)
def get_executive_health(
    service: AIOrchestrationService = Depends(get_ai_orchestration_service),
) -> OrchestrationHealthResponse:
    return service.validate_health()


cost_router = APIRouter(prefix="/api/ai-costs", tags=["ai-costs"])


@cost_router.get("/summary", response_model=AICostSummaryResponse)
def get_ai_cost_summary(
    service: AIOrchestrationService = Depends(get_ai_orchestration_service),
) -> AICostSummaryResponse:
    return service.get_cost_summary()
