from app.simulation_engine.metrics import get_simulation_engine_metrics
from app.simulation_engine.repository import SimulationBaselineRepository
from app.simulation_engine.schemas import SimulationHealthResponse


def build_simulation_health() -> SimulationHealthResponse:
    baseline = SimulationBaselineRepository().load_baseline()
    metrics = get_simulation_engine_metrics()
    return SimulationHealthResponse(
        status="ok",
        baseline_source=baseline.source,
        historical_queries=baseline.total_historical_queries,
        simulation_runs=metrics.simulation_runs,
    )
