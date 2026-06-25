from app.simulation_engine.schemas import PredefinedScenario, RouteMix, SimulationBaseline, SimulationScenarioInput


def _merge_route_mix(baseline: SimulationBaseline, scenario: SimulationScenarioInput) -> RouteMix:
    mix = baseline.route_mix
    values = {
        "business_pipeline_pct": scenario.business_pipeline_pct if scenario.business_pipeline_pct is not None else mix.business_pipeline_pct,
        "knowledge_service_pct": scenario.knowledge_service_pct if scenario.knowledge_service_pct is not None else mix.knowledge_service_pct,
        "conversation_memory_pct": scenario.conversation_memory_pct if scenario.conversation_memory_pct is not None else mix.conversation_memory_pct,
        "executive_reasoning_pct": scenario.executive_reasoning_pct if scenario.executive_reasoning_pct is not None else mix.executive_reasoning_pct,
        "legacy_chat_pct": scenario.legacy_chat_pct if scenario.legacy_chat_pct is not None else mix.legacy_chat_pct,
        "other_pct": mix.other_pct,
    }
    total = sum(values.values())
    if total <= 0:
        return RouteMix(**values)
    factor = 100.0 / total
    return RouteMix(**{key: round(value * factor, 2) for key, value in values.items()})


PREDEFINED_SCENARIOS: list[PredefinedScenario] = [
    PredefinedScenario(
        id="demo",
        name="Demo",
        description="Demostración controlada con pocos usuarios y alto uso determinista.",
        defaults=SimulationScenarioInput(
            scenario_id="demo",
            name="Demo",
            users=10,
            queries_per_user_day=6.0,
            business_pipeline_pct=50.0,
            knowledge_service_pct=30.0,
            conversation_memory_pct=10.0,
            executive_reasoning_pct=5.0,
            legacy_chat_pct=5.0,
            concurrency=2,
            peak_hours=4,
            working_days=5,
        ),
    ),
    PredefinedScenario(
        id="piloto",
        name="Piloto",
        description="Piloto interno con adopción moderada.",
        defaults=SimulationScenarioInput(
            scenario_id="piloto",
            name="Piloto",
            users=100,
            queries_per_user_day=8.0,
            concurrency=10,
            peak_hours=6,
            working_days=22,
        ),
    ),
    PredefinedScenario(
        id="produccion",
        name="Producción",
        description="Operación productiva estándar.",
        defaults=SimulationScenarioInput(
            scenario_id="produccion",
            name="Producción",
            users=500,
            queries_per_user_day=12.0,
            concurrency=50,
            peak_hours=8,
            working_days=22,
        ),
    ),
    PredefinedScenario(
        id="enterprise",
        name="Enterprise",
        description="Despliegue enterprise de alta escala.",
        defaults=SimulationScenarioInput(
            scenario_id="enterprise",
            name="Enterprise",
            users=1000,
            queries_per_user_day=15.0,
            concurrency=120,
            peak_hours=10,
            working_days=22,
        ),
    ),
    PredefinedScenario(
        id="custom",
        name="Hipótesis Personalizada",
        description="Parámetros definidos por el usuario.",
        defaults=SimulationScenarioInput(scenario_id="custom", name="Hipótesis Personalizada"),
    ),
]


class ScenarioEngine:
    def __init__(self, baseline: SimulationBaseline) -> None:
        self._baseline = baseline

    def list_predefined(self) -> list[PredefinedScenario]:
        enriched: list[PredefinedScenario] = []
        for item in PREDEFINED_SCENARIOS:
            if item.id == "custom":
                enriched.append(item)
                continue
            defaults = item.defaults.model_copy()
            defaults.business_pipeline_pct = defaults.business_pipeline_pct or self._baseline.route_mix.business_pipeline_pct
            defaults.knowledge_service_pct = defaults.knowledge_service_pct or self._baseline.route_mix.knowledge_service_pct
            defaults.conversation_memory_pct = defaults.conversation_memory_pct or self._baseline.route_mix.conversation_memory_pct
            defaults.executive_reasoning_pct = defaults.executive_reasoning_pct or self._baseline.route_mix.executive_reasoning_pct
            defaults.legacy_chat_pct = defaults.legacy_chat_pct or self._baseline.route_mix.legacy_chat_pct
            if defaults.queries_per_user_day == 12.0 and self._baseline.total_historical_queries > 0:
                defaults.queries_per_user_day = max(
                    self._baseline.total_historical_queries / max(defaults.users, 1) / max(defaults.working_days, 1),
                    1.0,
                )
            enriched.append(item.model_copy(update={"defaults": defaults}))
        return enriched

    def resolve(self, scenario: SimulationScenarioInput) -> tuple[SimulationScenarioInput, RouteMix]:
        route_mix = _merge_route_mix(self._baseline, scenario)
        return scenario, route_mix

    def get_predefined(self, scenario_id: str) -> SimulationScenarioInput | None:
        for item in PREDEFINED_SCENARIOS:
            if item.id == scenario_id:
                _, route_mix = self.resolve(item.defaults)
                return item.defaults.model_copy(
                    update={
                        "business_pipeline_pct": route_mix.business_pipeline_pct,
                        "knowledge_service_pct": route_mix.knowledge_service_pct,
                        "conversation_memory_pct": route_mix.conversation_memory_pct,
                        "executive_reasoning_pct": route_mix.executive_reasoning_pct,
                        "legacy_chat_pct": route_mix.legacy_chat_pct,
                    }
                )
        return None
