from datetime import datetime


class EnterpriseReasoningMetrics:
    reasoning_objects_total: int = 0
    reasoning_rules_executed: int = 0
    average_reasoning_confidence: float = 0.0
    average_findings: float = 0.0
    average_alerts: float = 0.0
    average_recommendations: float = 0.0
    last_reasoning_refresh: datetime | None = None
    reasoning_build_time: float = 0.0

    @classmethod
    def record_run(
        cls,
        *,
        objects_total: int,
        rules_executed: int,
        average_confidence: float,
        average_findings: float,
        average_alerts: float,
        average_recommendations: float,
        build_time_seconds: float,
        run_at: datetime,
    ) -> None:
        cls.reasoning_objects_total = objects_total
        cls.reasoning_rules_executed = rules_executed
        cls.average_reasoning_confidence = average_confidence
        cls.average_findings = average_findings
        cls.average_alerts = average_alerts
        cls.average_recommendations = average_recommendations
        cls.reasoning_build_time = build_time_seconds
        cls.last_reasoning_refresh = run_at

    @classmethod
    def snapshot(cls) -> dict:
        return {
            "reasoning_objects_total": cls.reasoning_objects_total,
            "reasoning_rules_executed": cls.reasoning_rules_executed,
            "average_reasoning_confidence": cls.average_reasoning_confidence,
            "average_findings": cls.average_findings,
            "average_alerts": cls.average_alerts,
            "average_recommendations": cls.average_recommendations,
            "last_reasoning_refresh": cls.last_reasoning_refresh,
            "reasoning_build_time": cls.reasoning_build_time,
        }

    @classmethod
    def reset_for_tests(cls) -> None:
        cls.reasoning_objects_total = 0
        cls.reasoning_rules_executed = 0
        cls.average_reasoning_confidence = 0.0
        cls.average_findings = 0.0
        cls.average_alerts = 0.0
        cls.average_recommendations = 0.0
        cls.last_reasoning_refresh = None
        cls.reasoning_build_time = 0.0
