from datetime import datetime


class BusinessOntologyMetrics:
    ontology_entities: int = 0
    ontology_pending: int = 0
    ontology_approved: int = 0
    ontology_rules: int = 0
    ontology_average_confidence: float = 0.0
    last_ontology_run: datetime | None = None

    @classmethod
    def record_run(
        cls,
        *,
        entities: int,
        pending: int,
        approved: int,
        rules: int,
        average_confidence: float,
        run_at: datetime,
    ) -> None:
        cls.ontology_entities = entities
        cls.ontology_pending = pending
        cls.ontology_approved = approved
        cls.ontology_rules = rules
        cls.ontology_average_confidence = round(average_confidence, 4)
        cls.last_ontology_run = run_at

    @classmethod
    def snapshot(cls) -> dict:
        return {
            "ontology_entities": cls.ontology_entities,
            "ontology_pending": cls.ontology_pending,
            "ontology_approved": cls.ontology_approved,
            "ontology_rules": cls.ontology_rules,
            "ontology_average_confidence": cls.ontology_average_confidence,
            "last_ontology_run": cls.last_ontology_run,
        }

    @classmethod
    def reset_for_tests(cls) -> None:
        cls.ontology_entities = 0
        cls.ontology_pending = 0
        cls.ontology_approved = 0
        cls.ontology_rules = 0
        cls.ontology_average_confidence = 0.0
        cls.last_ontology_run = None
