from sqlalchemy import text
from sqlalchemy.orm import Session


class BusinessAnalyticsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_route_counts(self) -> dict[str, int]:
        row = self.session.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total_requests,
                    COUNT(*) FILTER (WHERE handled_by = 'business_pipeline') AS business_pipeline,
                    COUNT(*) FILTER (WHERE handled_by = 'slot_clarification') AS slot_clarification,
                    COUNT(*) FILTER (WHERE handled_by = 'conversation_memory') AS conversation_memory,
                    COUNT(*) FILTER (WHERE handled_by = 'capability_discovery') AS capability_discovery,
                    COUNT(*) FILTER (WHERE handled_by = 'guided_fallback') AS guided_fallback,
                    COUNT(*) FILTER (WHERE handled_by = 'legacy_chat') AS legacy_chat
                FROM performance_metrics
                """
            )
        ).mappings().one()
        return {key: int(row[key]) for key in row.keys()}

    def get_success_rate(self) -> float:
        row = self.session.execute(
            text(
                """
                SELECT COALESCE(AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END), 0) AS success_rate
                FROM performance_metrics
                """
            )
        ).mappings().one()
        return float(row["success_rate"])

    def get_monthly_request_count(self) -> int:
        row = self.session.execute(
            text(
                """
                SELECT COUNT(*) AS monthly_requests
                FROM performance_metrics
                WHERE created_at >= NOW() - INTERVAL '30 days'
                """
            )
        ).mappings().one()
        return int(row["monthly_requests"])

    def get_performance_percentiles(self) -> dict[str, float]:
        row = self.session.execute(
            text(
                """
                SELECT
                    COALESCE(
                        percentile_cont(0.5) WITHIN GROUP (ORDER BY total_time_ms), 0
                    ) AS p50_ms,
                    COALESCE(
                        percentile_cont(0.95) WITHIN GROUP (ORDER BY total_time_ms), 0
                    ) AS p95_ms,
                    COALESCE(
                        percentile_cont(0.99) WITHIN GROUP (ORDER BY total_time_ms), 0
                    ) AS p99_ms,
                    COALESCE(AVG(intent_time_ms), 0) AS avg_intent_ms,
                    COALESCE(AVG(planner_time_ms), 0) AS avg_planner_ms,
                    COALESCE(AVG(executor_time_ms), 0) AS avg_executor_ms,
                    COALESCE(AVG(response_time_ms), 0) AS avg_response_ms,
                    COALESCE(AVG(total_time_ms), 0) AS avg_total_ms
                FROM performance_metrics
                """
            )
        ).mappings().one()
        return {key: float(row[key]) for key in row.keys()}

    def get_top_queries_with_routes(self, *, limit: int = 20) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    question,
                    handled_by AS route,
                    COUNT(*) AS count,
                    COALESCE(AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END), 0) AS success_rate
                FROM performance_metrics
                GROUP BY question, handled_by
                ORDER BY count DESC, question ASC, route ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [
            {
                "question": row["question"],
                "route": row["route"],
                "count": int(row["count"]),
                "success_rate": round(float(row["success_rate"]), 4),
            }
            for row in rows
        ]

    def get_top_routes(self, *, limit: int = 10) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    handled_by,
                    COALESCE(query_type, 'NONE') AS query_type,
                    COUNT(*) AS count,
                    COALESCE(AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END), 0) AS success_rate
                FROM performance_metrics
                GROUP BY handled_by, COALESCE(query_type, 'NONE')
                ORDER BY count DESC, handled_by ASC, query_type ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [
            {
                "handled_by": row["handled_by"],
                "query_type": row["query_type"],
                "count": int(row["count"]),
                "success_rate": round(float(row["success_rate"]), 4),
            }
            for row in rows
        ]
