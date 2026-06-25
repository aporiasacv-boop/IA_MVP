from datetime import datetime


class BusinessEntityMasterMetrics:
    """Métricas in-process de la última carga del catálogo maestro."""

    business_entities_loaded: int = 0
    duplicated_entities: int = 0
    last_entity_refresh: datetime | None = None

    @classmethod
    def record_refresh(
        cls,
        *,
        loaded: int,
        duplicated: int,
        refreshed_at: datetime | None = None,
    ) -> None:
        cls.business_entities_loaded = loaded
        cls.duplicated_entities = duplicated
        cls.last_entity_refresh = refreshed_at or datetime.now()

    @classmethod
    def snapshot(cls, *, total: int) -> dict:
        return {
            "business_entities_total": total,
            "business_entities_loaded": cls.business_entities_loaded,
            "duplicated_entities": cls.duplicated_entities,
            "last_entity_refresh": cls.last_entity_refresh,
        }

    @classmethod
    def reset_for_tests(cls) -> None:
        cls.business_entities_loaded = 0
        cls.duplicated_entities = 0
        cls.last_entity_refresh = None
