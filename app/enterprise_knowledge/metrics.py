from datetime import datetime


class EnterpriseKnowledgeMetrics:
    knowledge_objects_total: int = 0
    knowledge_build_time: float = 0.0
    knowledge_average_completeness: float = 0.0
    knowledge_average_confidence: float = 0.0
    knowledge_last_refresh: datetime | None = None

    @classmethod
    def record_run(
        cls,
        *,
        objects_total: int,
        build_time_seconds: float,
        average_completeness: float,
        average_confidence: float,
        run_at: datetime,
    ) -> None:
        cls.knowledge_objects_total = objects_total
        cls.knowledge_build_time = round(build_time_seconds, 4)
        cls.knowledge_average_completeness = round(average_completeness, 4)
        cls.knowledge_average_confidence = round(average_confidence, 4)
        cls.knowledge_last_refresh = run_at

    @classmethod
    def snapshot(cls) -> dict:
        return {
            "knowledge_objects_total": cls.knowledge_objects_total,
            "knowledge_build_time": cls.knowledge_build_time,
            "knowledge_average_completeness": cls.knowledge_average_completeness,
            "knowledge_average_confidence": cls.knowledge_average_confidence,
            "knowledge_last_refresh": cls.knowledge_last_refresh,
        }

    @classmethod
    def reset_for_tests(cls) -> None:
        cls.knowledge_objects_total = 0
        cls.knowledge_build_time = 0.0
        cls.knowledge_average_completeness = 0.0
        cls.knowledge_average_confidence = 0.0
        cls.knowledge_last_refresh = None
