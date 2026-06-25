from dataclasses import dataclass, field

from app.operational_metrics.schemas import OperationalQueryRecord


@dataclass
class OperationalFinOpsMetrics:
    records_total: int = 0
    cost_usd_total: float = 0.0
    avoided_cost_usd_total: float = 0.0
    llm_queries: int = 0
    real_token_records: int = 0
    provider_requests: dict[str, int] = field(default_factory=dict)

    def record(self, item: OperationalQueryRecord) -> None:
        self.records_total += 1
        self.cost_usd_total = round(self.cost_usd_total + item.cost_usd, 6)
        self.avoided_cost_usd_total = round(self.avoided_cost_usd_total + item.avoided_cost_usd, 6)
        if item.llm_used:
            self.llm_queries += 1
        if item.token_source == "api":
            self.real_token_records += 1
        if item.llm_provider:
            key = item.llm_provider.lower()
            self.provider_requests[key] = self.provider_requests.get(key, 0) + 1

    def snapshot(self) -> dict:
        return {
            "operational_records_total": self.records_total,
            "operational_cost_usd_total": self.cost_usd_total,
            "operational_avoided_cost_usd_total": self.avoided_cost_usd_total,
            "operational_llm_queries": self.llm_queries,
            "operational_real_token_records": self.real_token_records,
            "operational_provider_requests": dict(self.provider_requests),
        }


_metrics = OperationalFinOpsMetrics()


def get_operational_finops_metrics() -> OperationalFinOpsMetrics:
    return _metrics


def reset_operational_finops_metrics() -> None:
    global _metrics
    _metrics = OperationalFinOpsMetrics()
