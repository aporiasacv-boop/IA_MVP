from datetime import datetime


class EntityProfileMetrics:
    entity_profiles_total: int = 0
    average_profile_completeness: float = 0.0
    profile_generation_time: float = 0.0
    last_profile_refresh: datetime | None = None

    @classmethod
    def record_run(
        cls,
        *,
        profiles_total: int,
        average_completeness: float,
        generation_time_seconds: float,
        run_at: datetime,
    ) -> None:
        cls.entity_profiles_total = profiles_total
        cls.average_profile_completeness = round(average_completeness, 4)
        cls.profile_generation_time = round(generation_time_seconds, 4)
        cls.last_profile_refresh = run_at

    @classmethod
    def snapshot(cls) -> dict:
        return {
            "entity_profiles_total": cls.entity_profiles_total,
            "average_profile_completeness": cls.average_profile_completeness,
            "profile_generation_time": cls.profile_generation_time,
            "last_profile_refresh": cls.last_profile_refresh,
        }

    @classmethod
    def reset_for_tests(cls) -> None:
        cls.entity_profiles_total = 0
        cls.average_profile_completeness = 0.0
        cls.profile_generation_time = 0.0
        cls.last_profile_refresh = None
