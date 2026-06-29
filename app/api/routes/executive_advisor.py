from fastapi import APIRouter, Depends, Query

from app.api.deps import get_executive_advisor_service
from app.executive_advisor.schemas import ExecutiveAgendaResponse

router = APIRouter(prefix="/api/executive-advisor", tags=["executive-advisor"])


@router.get(
    "/agenda",
    response_model=ExecutiveAgendaResponse,
    summary="Agenda Ejecutiva",
    description=(
        "Construye una agenda priorizada usando exclusivamente información ya validada. "
        "No ejecuta SQL ni modifica respuestas empresariales."
    ),
)
def get_executive_agenda(
    session_id: str | None = Query(default=None),
    period: str | None = Query(default=None),
    scenario: str | None = Query(default=None),
    service=Depends(get_executive_advisor_service),
) -> ExecutiveAgendaResponse:
    return service.get_agenda(
        session_id=session_id,
        period=period,
        scenario=scenario,
    )
