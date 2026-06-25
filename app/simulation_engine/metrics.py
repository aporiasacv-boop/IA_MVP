from dataclasses import dataclass, field


@dataclass
class SimulationEngineMetrics:
    simulation_runs: int = 0
    most_used_scenario: dict[str, int] = field(default_factory=dict)
    provider_selected: dict[str, int] = field(default_factory=dict)
    projected_cost_total: float = 0.0
    projected_savings_total: float = 0.0

    def record_run(
        self,
        *,
        scenario_id: str,
        provider: str,
        projected_cost: float,
        projected_savings: float,
    ) -> None:
        self.simulation_runs += 1
        self.most_used_scenario[scenario_id] = self.most_used_scenario.get(scenario_id, 0) + 1
        self.provider_selected[provider] = self.provider_selected.get(provider, 0) + 1
        self.projected_cost_total = round(self.projected_cost_total + projected_cost, 4)
        self.projected_savings_total = round(self.projected_savings_total + projected_savings, 4)

    @property
    def average_projected_cost(self) -> float:
        if self.simulation_runs <= 0:
            return 0.0
        return round(self.projected_cost_total / self.simulation_runs, 4)

    @property
    def average_projected_savings(self) -> float:
        if self.simulation_runs <= 0:
            return 0.0
        return round(self.projected_savings_total / self.simulation_runs, 4)

    def snapshot(self) -> dict:
        top_scenario = max(self.most_used_scenario, key=self.most_used_scenario.get) if self.most_used_scenario else ""
        top_provider = max(self.provider_selected, key=self.provider_selected.get) if self.provider_selected else ""
        return {
            "simulation_runs": self.simulation_runs,
            "most_used_scenario": top_scenario,
            "provider_selected": top_provider,
            "average_projected_cost": self.average_projected_cost,
            "average_projected_savings": self.average_projected_savings,
        }


_metrics = SimulationEngineMetrics()


def get_simulation_engine_metrics() -> SimulationEngineMetrics:
    return _metrics


def reset_simulation_engine_metrics() -> None:
    global _metrics
    _metrics = SimulationEngineMetrics()
