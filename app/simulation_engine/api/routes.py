from fastapi import APIRouter, Depends

from app.api.deps import get_simulation_engine_service_dep
from app.simulation_engine.schemas import (
    SimulationComparisonResponse,
    SimulationRecommendationsResponse,
    SimulationRunResponse,
    SimulationScenarioInput,
    SimulationScenariosResponse,
)
from app.simulation_engine.service import SimulationEngineService

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.get("/scenarios", response_model=SimulationScenariosResponse)
def simulation_scenarios(
    service: SimulationEngineService = Depends(get_simulation_engine_service_dep),
) -> SimulationScenariosResponse:
    return service.list_scenarios()


@router.post("/run", response_model=SimulationRunResponse)
def simulation_run(
    scenario: SimulationScenarioInput,
    service: SimulationEngineService = Depends(get_simulation_engine_service_dep),
) -> SimulationRunResponse:
    return service.run(scenario)


@router.get("/comparison", response_model=SimulationComparisonResponse)
def simulation_comparison(
    service: SimulationEngineService = Depends(get_simulation_engine_service_dep),
) -> SimulationComparisonResponse:
    return service.comparison()


@router.get("/recommendations", response_model=SimulationRecommendationsResponse)
def simulation_recommendations(
    service: SimulationEngineService = Depends(get_simulation_engine_service_dep),
) -> SimulationRecommendationsResponse:
    return service.recommendations()
