from fastapi import APIRouter, Depends

from app.api.deps import get_insights_engine
from app.schemas.insights import InsightResponse, InsightsResumenResponse
from app.services.insights_engine import InsightsEngine

router = APIRouter(prefix="/api", tags=["insights"])


@router.get(
    "/insights",
    response_model=list[InsightResponse],
    summary="Insights empresariales",
    description=(
        "Genera insights ejecutivos mediante reglas deterministicas "
        "sobre el datamart. No utiliza IA."
    ),
)
def get_insights(
    engine: InsightsEngine = Depends(get_insights_engine),
) -> list[InsightResponse]:
    return engine.generate_insights()


@router.get(
    "/insights/resumen",
    response_model=InsightsResumenResponse,
    summary="Resumen de insights",
    description="Conteo de insights por nivel de severidad.",
)
def get_insights_resumen(
    engine: InsightsEngine = Depends(get_insights_engine),
) -> InsightsResumenResponse:
    return engine.generate_resumen()
