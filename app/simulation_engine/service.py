from app.simulation_engine.decision_engine import DecisionEngine
from app.simulation_engine.forecast_engine import SimulationForecastEngine
from app.simulation_engine.metrics import get_simulation_engine_metrics
from app.simulation_engine.repository import SimulationBaselineRepository
from app.simulation_engine.scenario_engine import ScenarioEngine
from app.simulation_engine.schemas import (
    SimulationComparisonResponse,
    SimulationRecommendationsResponse,
    SimulationRunResponse,
    SimulationScenarioInput,
    SimulationScenariosResponse,
)

_last_run: SimulationRunResponse | None = None


class SimulationEngineService:
    def __init__(self) -> None:
        self._baseline_repo = SimulationBaselineRepository()

    def _baseline(self):
        return self._baseline_repo.load_baseline()

    def list_scenarios(self) -> SimulationScenariosResponse:
        baseline = self._baseline()
        return SimulationScenariosResponse(
            baseline=baseline,
            predefined=ScenarioEngine(baseline).list_predefined(),
        )

    def run(self, scenario: SimulationScenarioInput) -> SimulationRunResponse:
        global _last_run
        baseline = self._baseline()
        scenario_engine = ScenarioEngine(baseline)
        if scenario.scenario_id != "custom":
            predefined = scenario_engine.get_predefined(scenario.scenario_id)
            if predefined is not None:
                merged = predefined.model_dump()
                merged.update(scenario.model_dump(exclude_unset=True))
                scenario = SimulationScenarioInput(**merged)
        resolved, route_mix = scenario_engine.resolve(scenario)
        forecast = SimulationForecastEngine(baseline)
        metrics = forecast.simulate(resolved, route_mix)
        providers = forecast.compare_providers(resolved, route_mix)
        response = SimulationRunResponse(
            scenario_id=resolved.scenario_id,
            scenario_name=resolved.name,
            baseline_source=baseline.source,
            metrics=metrics,
            provider_comparison=providers,
            assumptions={
                "baseline_source": baseline.source,
                "historical_queries": str(baseline.total_historical_queries),
                "llm_provider": resolved.llm_provider,
                "working_days": str(resolved.working_days),
                "data_source": "operational_metrics_finops",
            },
        )
        get_simulation_engine_metrics().record_run(
            scenario_id=resolved.scenario_id,
            provider=resolved.llm_provider,
            projected_cost=metrics.cost_usd,
            projected_savings=metrics.avoided_cost_usd,
        )
        _last_run = response
        return response

    def comparison(self, scenario: SimulationScenarioInput | None = None) -> SimulationComparisonResponse:
        if scenario is not None:
            run = self.run(scenario)
            providers = run.provider_comparison
            scenario_name = run.scenario_name
        elif _last_run is not None:
            providers = _last_run.provider_comparison
            scenario_name = _last_run.scenario_name
        else:
            baseline = self._baseline()
            default = ScenarioEngine(baseline).get_predefined("piloto")
            run = self.run(default or SimulationScenarioInput())
            providers = run.provider_comparison
            scenario_name = run.scenario_name
        return DecisionEngine(self._baseline()).build_comparison(scenario_name, providers)

    def recommendations(self, scenario: SimulationScenarioInput | None = None) -> SimulationRecommendationsResponse:
        if scenario is not None:
            run = self.run(scenario)
        elif _last_run is not None:
            run = _last_run
        else:
            baseline = self._baseline()
            default = ScenarioEngine(baseline).get_predefined("piloto")
            run = self.run(default or SimulationScenarioInput())
        return DecisionEngine(self._baseline()).build_recommendations(
            scenario=SimulationScenarioInput(
                scenario_id=run.scenario_id,
                name=run.scenario_name,
                llm_provider=run.assumptions.get("llm_provider", "openai"),
                users=100,
            ),
            metrics=run.metrics,
            providers=run.provider_comparison,
        )

    def health(self):
        from app.simulation_engine.health import build_simulation_health

        return build_simulation_health()


_service: SimulationEngineService | None = None


def get_simulation_engine_service() -> SimulationEngineService:
    global _service
    if _service is None:
        _service = SimulationEngineService()
    return _service


def reset_simulation_engine_service() -> None:
    global _service, _last_run
    _service = None
    _last_run = None
