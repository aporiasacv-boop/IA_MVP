from app.enterprise_decision.repository import DecisionContext
from app.enterprise_decision.schemas import FinancialImpact, ScenarioConsidered


class FinancialAnalyzer:
    def analyze(self, context: DecisionContext) -> tuple[FinancialImpact, list[ScenarioConsidered]]:
        overview = context.finops_overview
        run_metrics = context.simulation_run.get("metrics", {}) if context.simulation_run else {}
        cost_usd = float(run_metrics.get("cost_usd", overview.get("total_cost_usd", 0.0)))
        avoided = float(run_metrics.get("avoided_cost_usd", overview.get("total_avoided_cost_usd", 0.0)))
        impact = FinancialImpact(
            cost_usd=round(cost_usd, 4),
            cost_mxn=round(float(run_metrics.get("cost_mxn", overview.get("total_cost_mxn", 0.0))), 4),
            avoided_cost_usd=round(avoided, 4),
            roi_pct=float(run_metrics.get("roi_pct", 0.0)),
            llm_avoidance_rate=float(
                run_metrics.get("llm_avoidance_rate", overview.get("llm_avoidance_rate", 0.0))
            ),
            monthly_projection_usd=round(cost_usd, 4),
        )
        scenarios: list[ScenarioConsidered] = []
        if context.simulation_run:
            metrics = context.simulation_run.get("metrics", {})
            scenarios.append(
                ScenarioConsidered(
                    scenario_id=context.simulation_run.get("scenario_id", "piloto"),
                    scenario_name=context.simulation_run.get("scenario_name", "Piloto"),
                    cost_usd=float(metrics.get("cost_usd", 0.0)),
                    avoided_cost_usd=float(metrics.get("avoided_cost_usd", 0.0)),
                    llm_avoidance_rate=float(metrics.get("llm_avoidance_rate", 0.0)),
                )
            )
        return impact, scenarios
