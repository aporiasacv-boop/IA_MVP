import time
from datetime import datetime
from decimal import Decimal

from app.business_ontology.metrics import BusinessOntologyMetrics
from app.business_ontology.repository import BusinessOntologyRepository
from app.business_ontology.rules_engine import OntologyEntityContext, generate_ontology_suggestions
from app.business_ontology.schemas import OntologyGenerationResult


class OntologyEngine:
    def __init__(self, repository: BusinessOntologyRepository) -> None:
        self._repository = repository

    def run_idempotent(self, *, now: datetime | None = None) -> OntologyGenerationResult:
        started = time.perf_counter()
        timestamp = now or datetime.now()

        types_seeded = self._repository.seed_taxonomy_if_empty(now=timestamp)
        rules_seeded = self._repository.seed_rules_if_empty(now=timestamp)
        type_map = self._repository.get_type_code_map()

        active_rules = self._repository.fetch_active_rules()
        rule_tuples = [
            (
                row["rule_code"],
                row["concept_category"],
                row["type_code"],
                dict(row["conditions_json"] or {}),
                Decimal(str(row["score_weight"])),
            )
            for row in active_rules
        ]

        inserted = 0
        updated = 0
        entities_processed = 0

        for row in self._repository.fetch_entity_contexts():
            ctx = OntologyEntityContext(
                canonical_id=int(row["canonical_id"]),
                canonical_name=row["canonical_name"],
                primary_rfc=row.get("primary_rfc"),
                normalized_name=row["normalized_name"],
                alias_count=int(row["alias_count"]),
                total_movements=int(row["total_movements"] or 0),
                total_amount=Decimal(str(row["total_amount"] or 0)),
                debit_amount=Decimal(str(row["debit_amount"] or 0)),
                credit_amount=Decimal(str(row["credit_amount"] or 0)),
                debit_credit_ratio=Decimal(str(row["debit_credit_ratio"]))
                if row.get("debit_credit_ratio") is not None
                else None,
                related_accounts_count=int(row["related_accounts_count"] or 0),
                related_counterparties_count=int(row["related_counterparties_count"] or 0),
                active_months=int(row["active_months"] or 0),
                dimensions_used=list(row.get("dimensions_used") or []),
                top_accounts=list(row.get("top_accounts") or []),
                top_counterparties=list(row.get("top_counterparties") or []),
                currencies=list(row.get("currencies") or []),
            )
            entities_processed += 1
            suggestions = generate_ontology_suggestions(ctx, rule_tuples)
            for suggestion in suggestions:
                type_id = type_map.get((suggestion.concept_category, suggestion.type_code))
                if type_id is None:
                    continue
                is_new = self._repository.upsert_assignment(
                    canonical_id=suggestion.canonical_id,
                    concept_category=suggestion.concept_category,
                    type_id=type_id,
                    rule_code=suggestion.rule_code,
                    evidence_json=suggestion.evidence,
                    score=suggestion.score,
                    confidence=suggestion.confidence,
                    now=timestamp,
                )
                if is_new:
                    inserted += 1
                else:
                    updated += 1

        self._repository.session.commit()
        elapsed = round(time.perf_counter() - started, 4)

        BusinessOntologyMetrics.record_run(
            entities=self._repository.count_entities_with_assignments(),
            pending=self._repository.count_assignments(status="pending"),
            approved=self._repository.count_assignments(status="approved"),
            rules=self._repository.count_rules(),
            average_confidence=self._repository.average_confidence(),
            run_at=timestamp,
        )

        return OntologyGenerationResult(
            types_seeded=types_seeded,
            rules_seeded=rules_seeded,
            suggestions_inserted=inserted,
            suggestions_updated=updated,
            entities_processed=entities_processed,
            generation_time_seconds=elapsed,
        )
