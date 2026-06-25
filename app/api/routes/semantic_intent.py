from fastapi import APIRouter, Depends

from app.api.deps import get_semantic_intent_service
from app.semantic_intent.schemas import (
    BusinessExecutionPlan,
    SemanticParseRequest,
    SemanticParseResult,
    SemanticPlanRequest,
    SemanticStatisticsResponse,
    VerbCatalogResponse,
)
from app.semantic_intent.service import SemanticIntentService

router = APIRouter(prefix="/api/semantic-intent", tags=["semantic-intent"])


@router.get("/verbs", response_model=VerbCatalogResponse)
def get_semantic_verbs(
    service: SemanticIntentService = Depends(get_semantic_intent_service),
) -> VerbCatalogResponse:
    return service.get_verbs()


@router.get("/statistics", response_model=SemanticStatisticsResponse)
def get_semantic_statistics(
    service: SemanticIntentService = Depends(get_semantic_intent_service),
) -> SemanticStatisticsResponse:
    return service.get_statistics()


@router.post("/parse", response_model=SemanticParseResult)
def parse_semantic_intent(
    request: SemanticParseRequest,
    service: SemanticIntentService = Depends(get_semantic_intent_service),
) -> SemanticParseResult:
    return service.parse(request)


@router.post("/plan", response_model=BusinessExecutionPlan)
def plan_semantic_execution(
    request: SemanticPlanRequest,
    service: SemanticIntentService = Depends(get_semantic_intent_service),
) -> BusinessExecutionPlan:
    return service.plan(request)
