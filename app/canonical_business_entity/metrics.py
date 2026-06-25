from datetime import datetime


class CanonicalEntityMetrics:
    canonical_entities_total: int = 0
    canonical_matches: int = 0
    pending_matches: int = 0
    automatic_suggestions: int = 0
    last_suggestion_run: datetime | None = None

    @classmethod
    def record_run(
        cls,
        *,
        canonical_total: int,
        canonical_matches: int,
        pending_matches: int,
        automatic_suggestions: int,
        run_at: datetime | None = None,
    ) -> None:
        cls.canonical_entities_total = canonical_total
        cls.canonical_matches = canonical_matches
        cls.pending_matches = pending_matches
        cls.automatic_suggestions = automatic_suggestions
        cls.last_suggestion_run = run_at or datetime.now()

    @classmethod
    def snapshot(cls) -> dict:
        return {
            "canonical_entities_total": cls.canonical_entities_total,
            "canonical_matches": cls.canonical_matches,
            "pending_matches": cls.pending_matches,
            "automatic_suggestions": cls.automatic_suggestions,
        }

    @classmethod
    def reset_for_tests(cls) -> None:
        cls.canonical_entities_total = 0
        cls.canonical_matches = 0
        cls.pending_matches = 0
        cls.automatic_suggestions = 0
        cls.last_suggestion_run = None
