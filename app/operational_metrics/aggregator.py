from collections import defaultdict
from datetime import datetime, timezone

from app.operational_metrics.cost_engine import is_knowledge_route, is_llm_route, is_pipeline_route
from app.operational_metrics.schemas import (
    CostBreakdownItem,
    FinOpsCostsResponse,
    FinOpsOverviewResponse,
    FinOpsProvidersResponse,
    FinOpsSavingsResponse,
    FinOpsTrendsResponse,
    OperationalQueryRecord,
    ProviderComparisonItem,
    SavingsByRouteItem,
    TrendPoint,
)


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


class OperationalMetricsAggregator:
    def __init__(self, records: list[OperationalQueryRecord]) -> None:
        self._records = records

    def overview(self) -> FinOpsOverviewResponse:
        total = len(self._records)
        llm_queries = sum(1 for r in self._records if r.llm_used)
        deterministic = total - llm_queries
        total_cost = sum(r.cost_usd for r in self._records)
        total_avoided = sum(r.avoided_cost_usd for r in self._records)
        real_token = sum(1 for r in self._records if r.token_source == "api")
        estimated_token = sum(1 for r in self._records if r.token_source == "estimated")
        now = datetime.now(timezone.utc)
        today_key = now.strftime("%Y-%m-%d")
        month_key = now.strftime("%Y-%m")
        cost_today = sum(r.cost_usd for r in self._records if r.timestamp.strftime("%Y-%m-%d") == today_key)
        cost_month = sum(r.cost_usd for r in self._records if r.timestamp.strftime("%Y-%m") == month_key)
        sessions = {r.session_id for r in self._records if r.session_id}
        users = {r.user_id for r in self._records if r.user_id}
        llm_cost = sum(r.cost_usd for r in self._records if r.llm_used)
        return FinOpsOverviewResponse(
            total_queries=total,
            total_cost_usd=round(total_cost, 4),
            total_cost_mxn=round(sum(r.cost_mxn for r in self._records), 4),
            cost_today_usd=round(cost_today, 4),
            cost_month_usd=round(cost_month, 4),
            cost_year_projected_usd=round(cost_month * 12, 4),
            avg_cost_per_query_usd=round(total_cost / total, 6) if total else 0.0,
            avg_cost_per_session_usd=round(total_cost / len(sessions), 6) if sessions else 0.0,
            avg_cost_per_user_usd=round(total_cost / len(users), 6) if users else 0.0,
            llm_queries=llm_queries,
            deterministic_queries=deterministic,
            llm_avoidance_rate=_safe_rate(deterministic, total),
            knowledge_avoidance_rate=_safe_rate(sum(1 for r in self._records if is_knowledge_route(r.handled_by)), total),
            pipeline_avoidance_rate=_safe_rate(sum(1 for r in self._records if is_pipeline_route(r.handled_by)), total),
            total_avoided_cost_usd=round(total_avoided, 4),
            accumulated_savings_usd=round(total_avoided, 4),
            real_token_queries=real_token,
            estimated_token_queries=estimated_token,
            real_cost_share=round(llm_cost / total_cost, 4) if total_cost > 0 else 0.0,
        )

    def costs(self) -> FinOpsCostsResponse:
        return FinOpsCostsResponse(
            by_query=self._group("request_id", lambda r: r.request_id, include_tokens=True),
            by_session=self._group("session", lambda r: r.session_id or "sin_sesion"),
            by_user=self._group("user", lambda r: r.user_id or "anonimo"),
            by_day=self._group("day", lambda r: r.timestamp.strftime("%Y-%m-%d")),
            by_month=self._group("month", lambda r: r.timestamp.strftime("%Y-%m")),
            by_year=self._group("year", lambda r: r.timestamp.strftime("%Y")),
            by_channel=self._group("channel", lambda r: r.channel),
            by_handled_by=self._group("handled_by", lambda r: r.handled_by),
            by_query_type=self._group("query_type", lambda r: r.query_type or "desconocido"),
            by_provider=self._group("provider", lambda r: r.provider),
            by_model=self._group("model", lambda r: r.model or "sin_modelo"),
            by_llm=self._group("llm", lambda r: r.llm_provider or "sin_llm"),
        )

    def providers(self) -> FinOpsProvidersResponse:
        buckets: dict[str, dict] = defaultdict(
            lambda: {
                "requests": 0,
                "tokens_input": 0,
                "tokens_output": 0,
                "cost_usd": 0.0,
                "latency_total": 0.0,
            }
        )
        for record in self._records:
            if not record.llm_used:
                continue
            key = (record.llm_provider or record.provider or "desconocido").lower()
            bucket = buckets[key]
            bucket["requests"] += 1
            bucket["tokens_input"] += record.input_tokens
            bucket["tokens_output"] += record.output_tokens
            bucket["cost_usd"] += record.cost_usd
            bucket["latency_total"] += record.response_time_ms
        total_requests = sum(item["requests"] for item in buckets.values())
        providers: list[ProviderComparisonItem] = []
        for provider, data in sorted(buckets.items()):
            requests = data["requests"]
            providers.append(
                ProviderComparisonItem(
                    provider=provider,
                    requests=requests,
                    tokens_input=data["tokens_input"],
                    tokens_output=data["tokens_output"],
                    total_tokens=data["tokens_input"] + data["tokens_output"],
                    cost_usd=round(data["cost_usd"], 6),
                    average_latency_ms=round(data["latency_total"] / requests, 2) if requests else 0.0,
                    participation_pct=round((requests / total_requests) * 100, 2) if total_requests else 0.0,
                )
            )
        for name in ("openai", "claude", "ollama", "mock"):
            if name not in buckets:
                providers.append(
                    ProviderComparisonItem(
                        provider=name,
                        requests=0,
                        tokens_input=0,
                        tokens_output=0,
                        total_tokens=0,
                        cost_usd=0.0,
                        average_latency_ms=0.0,
                        participation_pct=0.0,
                    )
                )
        return FinOpsProvidersResponse(providers=providers, total_requests=total_requests)

    def savings(self) -> FinOpsSavingsResponse:
        overview = self.overview()
        by_route_map: dict[str, dict] = defaultdict(lambda: {"queries": 0, "avoided": 0.0})
        for record in self._records:
            bucket = by_route_map[record.handled_by]
            bucket["queries"] += 1
            bucket["avoided"] += record.avoided_cost_usd
        total_avoided = overview.total_avoided_cost_usd
        by_route = [
            SavingsByRouteItem(
                handled_by=route,
                queries=data["queries"],
                avoided_cost_usd=round(data["avoided"], 4),
                share_pct=round((data["avoided"] / total_avoided) * 100, 2) if total_avoided else 0.0,
            )
            for route, data in sorted(by_route_map.items(), key=lambda item: -item[1]["avoided"])
        ]
        return FinOpsSavingsResponse(
            llm_avoidance_rate=overview.llm_avoidance_rate,
            knowledge_avoidance_rate=overview.knowledge_avoidance_rate,
            pipeline_avoidance_rate=overview.pipeline_avoidance_rate,
            total_avoided_cost_usd=overview.total_avoided_cost_usd,
            accumulated_savings_usd=overview.accumulated_savings_usd,
            by_route=by_route,
        )

    def trends(self) -> FinOpsTrendsResponse:
        daily_map: dict[str, dict] = defaultdict(
            lambda: {"queries": 0, "cost": 0.0, "avoided": 0.0, "llm": 0, "latency": 0.0}
        )
        monthly_map: dict[str, dict] = defaultdict(
            lambda: {"queries": 0, "cost": 0.0, "avoided": 0.0, "llm": 0, "latency": 0.0}
        )
        for record in self._records:
            day = record.timestamp.strftime("%Y-%m-%d")
            month = record.timestamp.strftime("%Y-%m")
            for key, bucket in ((day, daily_map[day]), (month, monthly_map[month])):
                bucket["queries"] += 1
                bucket["cost"] += record.cost_usd
                bucket["avoided"] += record.avoided_cost_usd
                bucket["llm"] += 1 if record.llm_used else 0
                bucket["latency"] += record.response_time_ms
        return FinOpsTrendsResponse(
            daily=self._trend_points(daily_map),
            monthly=self._trend_points(monthly_map),
        )

    def _group(
        self,
        dimension: str,
        key_fn,
        *,
        include_tokens: bool = False,
    ) -> list[CostBreakdownItem]:
        buckets: dict[str, dict] = defaultdict(lambda: {"requests": 0, "cost_usd": 0.0, "cost_mxn": 0.0, "tokens": 0})
        for record in self._records:
            key = key_fn(record) or "desconocido"
            bucket = buckets[str(key)]
            bucket["requests"] += 1
            bucket["cost_usd"] += record.cost_usd
            bucket["cost_mxn"] += record.cost_mxn
            if include_tokens:
                bucket["tokens"] += record.total_tokens
        return [
            CostBreakdownItem(
                dimension=dimension,
                key=key,
                requests=data["requests"],
                cost_usd=round(data["cost_usd"], 6),
                cost_mxn=round(data["cost_mxn"], 6),
                tokens=data["tokens"],
            )
            for key, data in sorted(buckets.items(), key=lambda item: -item[1]["cost_usd"])
        ]

    @staticmethod
    def _trend_points(bucket_map: dict[str, dict]) -> list[TrendPoint]:
        points: list[TrendPoint] = []
        for period in sorted(bucket_map.keys()):
            data = bucket_map[period]
            queries = data["queries"]
            points.append(
                TrendPoint(
                    period=period,
                    queries=queries,
                    cost_usd=round(data["cost"], 4),
                    avoided_cost_usd=round(data["avoided"], 4),
                    llm_queries=data["llm"],
                    avg_latency_ms=round(data["latency"] / queries, 2) if queries else 0.0,
                )
            )
        return points
