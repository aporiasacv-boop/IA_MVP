from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from app.canonical_business_entity.constants import RULE_SINGLETON_BOOTSTRAP
from app.canonical_business_entity.matcher import generate_match_candidates
from app.canonical_business_entity.metrics import CanonicalEntityMetrics
from app.canonical_business_entity.repository import CanonicalBusinessEntityRepository
from app.canonical_business_entity.schemas import SuggestionRunResult
from app.models.business_entity_master import BusinessEntityMaster


class CanonicalSuggestionEngine:
    def __init__(self, repository: CanonicalBusinessEntityRepository) -> None:
        self._repository = repository

    def run_idempotent(self, *, now: datetime | None = None) -> SuggestionRunResult:
        timestamp = now or datetime.now()
        singletons_created = 0
        resolutions_created = 0
        suggestions_inserted = 0
        suggestions_updated = 0

        unresolved_ids = set(self._repository.get_unresolved_commercial_entity_ids())
        if unresolved_ids:
            rows = self._repository.session.scalars(
                select(BusinessEntityMaster).where(
                    BusinessEntityMaster.entity_id.in_(unresolved_ids)
                )
            ).all()
            for entity in rows:
                self._repository.create_singleton_canonical(entity, now=timestamp)
                singletons_created += 1
                resolutions_created += 1
            self._repository.session.commit()

        commercial_entities = self._repository.fetch_commercial_entities()
        candidates = generate_match_candidates(commercial_entities)
        for match in candidates:
            is_new = self._repository.upsert_suggestion(
                source_entity_id=match.source_entity_id,
                candidate_entity_id=match.candidate_entity_id,
                rule_used=match.rule_used,
                score=match.score,
                now=timestamp,
            )
            if is_new:
                suggestions_inserted += 1
            else:
                suggestions_updated += 1
        self._repository.session.commit()

        stats = self._build_stats()
        CanonicalEntityMetrics.record_run(
            canonical_total=stats["canonical_entities_total"],
            canonical_matches=stats["canonical_matches"],
            pending_matches=stats["pending_matches"],
            automatic_suggestions=stats["automatic_suggestions"],
            run_at=timestamp,
        )

        return SuggestionRunResult(
            singletons_created=singletons_created,
            resolutions_created=resolutions_created,
            suggestions_inserted=suggestions_inserted,
            suggestions_updated=suggestions_updated,
        )

    def _build_stats(self) -> dict:
        return {
            "canonical_entities_total": self._repository.count_canonical(),
            "canonical_matches": self._repository.count_canonical_matches(),
            "pending_matches": self._repository.count_pending_suggestions(),
            "automatic_suggestions": self._repository.count_automatic_suggestions(),
        }
