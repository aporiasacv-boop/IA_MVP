from sqlalchemy import text
from sqlalchemy.orm import Session


class OperationalAuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_overview_counts(self) -> dict:
        row = self.session.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total_requests,
                    COUNT(*) FILTER (WHERE success) AS total_successes,
                    COUNT(*) FILTER (WHERE NOT success) AS total_failures,
                    COUNT(*) FILTER (WHERE handled_by = 'business_pipeline') AS business_pipeline,
                    COUNT(*) FILTER (WHERE handled_by = 'conversation_memory') AS conversation_memory,
                    COUNT(*) FILTER (WHERE handled_by = 'slot_clarification') AS slot_clarification,
                    COUNT(*) FILTER (WHERE handled_by = 'capability_discovery') AS capability_discovery,
                    COUNT(*) FILTER (WHERE handled_by = 'guided_fallback') AS guided_fallback,
                    COUNT(*) FILTER (WHERE handled_by = 'legacy_chat') AS legacy_chat,
                    COALESCE(AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END), 0) AS success_rate
                FROM performance_metrics
                """
            )
        ).mappings().one()
        return {key: row[key] for key in row.keys()}

    def get_coverage_gaps(self, *, limit: int = 50) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT question, handled_by AS route, COUNT(*) AS count
                FROM performance_metrics
                WHERE handled_by IN ('legacy_chat', 'guided_fallback')
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
            }
            for row in rows
        ]

    def get_top_routes(self, *, limit: int = 20) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    handled_by AS route,
                    COUNT(*) AS count
                FROM performance_metrics
                GROUP BY handled_by
                ORDER BY count DESC, route ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [
            {"route": row["route"], "count": int(row["count"])}
            for row in rows
        ]

    def get_top_failures(self, *, limit: int = 50) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT question, handled_by AS route, COUNT(*) AS frequency
                FROM performance_metrics
                WHERE NOT success
                GROUP BY question, handled_by
                ORDER BY frequency DESC, question ASC, route ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [
            {
                "question": row["question"],
                "route": row["route"],
                "frequency": int(row["frequency"]),
            }
            for row in rows
        ]

    def get_adoption_counts(self) -> dict[str, int]:
        row = self.session.execute(
            text(
                """
                SELECT
                    COUNT(*) FILTER (
                        WHERE COALESCE(suggested_questions_count, 0) > 0
                    ) AS suggested_questions_usage,
                    COUNT(*) FILTER (
                        WHERE handled_by = 'conversation_memory'
                    ) AS conversation_memory_usage,
                    COUNT(*) FILTER (
                        WHERE handled_by = 'slot_clarification'
                    ) AS slot_clarification_usage,
                    COUNT(*) FILTER (
                        WHERE handled_by = 'capability_discovery'
                    ) AS capability_discovery_usage
                FROM performance_metrics
                """
            )
        ).mappings().one()
        return {key: int(row[key]) for key in row.keys()}
