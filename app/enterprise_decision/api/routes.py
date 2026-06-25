from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.enterprise_decision.decision_engine import InsufficientEvidenceError
from app.enterprise_decision.schemas import (
    DecisionRecommendRequest,
    DecisionSchemaResponse,
    DecisionStatisticsResponse,
    EnterpriseDecisionPackage,
)
from app.enterprise_decision.service import EnterpriseDecisionService, get_enterprise_decision_service

router = APIRouter(prefix="/api/decision", tags=["decision"])


def get_enterprise_decision_service_dep() -> EnterpriseDecisionService:
    return get_enterprise_decision_service()


@router.post("/recommend", response_model=EnterpriseDecisionPackage)
def decision_recommend(
    request: DecisionRecommendRequest,
    session: Session = Depends(get_db),
    service: EnterpriseDecisionService = Depends(get_enterprise_decision_service_dep),
) -> EnterpriseDecisionPackage:
    try:
        return service.recommend(request, session=session)
    except InsufficientEvidenceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/schema", response_model=DecisionSchemaResponse)
def decision_schema(
    service: EnterpriseDecisionService = Depends(get_enterprise_decision_service_dep),
) -> DecisionSchemaResponse:
    return service.get_schema()


@router.get("/statistics", response_model=DecisionStatisticsResponse)
def decision_statistics(
    service: EnterpriseDecisionService = Depends(get_enterprise_decision_service_dep),
) -> DecisionStatisticsResponse:
    return service.get_statistics()


@router.get("/example", response_model=EnterpriseDecisionPackage)
def decision_example(
    session: Session = Depends(get_db),
    service: EnterpriseDecisionService = Depends(get_enterprise_decision_service_dep),
) -> EnterpriseDecisionPackage:
    try:
        return service.get_example(session=session)
    except InsufficientEvidenceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
