from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.business_ontology.constants import CONCEPT_NATURE, STATUS_PENDING
from app.business_ontology.taxonomy import INITIAL_TAXONOMY, RuleSeed, TaxonomyTypeSeed, build_rule_seeds
from app.models.business_ontology import BusinessOntologyAssignment, BusinessOntologyRule, BusinessOntologyType
from app.models.business_entity_profile import BusinessEntityProfile
from app.models.canonical_business_entity import CanonicalBusinessEntity


class BusinessOntologyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_types(self) -> int:
        return self.session.scalar(select(func.count()).select_from(BusinessOntologyType)) or 0

    def count_rules(self) -> int:
        return self.session.scalar(
            select(func.count()).select_from(BusinessOntologyRule).where(BusinessOntologyRule.is_active.is_(True))
        ) or 0

    def count_assignments(self, *, status: str | None = None) -> int:
        query = select(func.count()).select_from(BusinessOntologyAssignment)
        if status:
            query = query.where(BusinessOntologyAssignment.status == status)
        return self.session.scalar(query) or 0

    def count_entities_with_assignments(self) -> int:
        row = self.session.execute(
            text("SELECT COUNT(DISTINCT canonical_id) FROM business_ontology_assignment")
        ).scalar_one()
        return int(row)

    def average_confidence(self) -> float:
        value = self.session.scalar(select(func.avg(BusinessOntologyAssignment.confidence)))
        return round(float(value or 0), 4)

    def count_entities_without_suggestions(self) -> int:
        row = self.session.execute(
            text(
                """
                SELECT COUNT(*)
                FROM canonical_business_entity cbe
                LEFT JOIN business_ontology_assignment boa ON boa.canonical_id = cbe.canonical_id
                WHERE boa.assignment_id IS NULL
                """
            )
        ).scalar_one()
        return int(row)

    def seed_taxonomy_if_empty(self, *, now: datetime) -> int:
        existing = self.count_types()
        if existing > 0:
            return 0
        for seed in INITIAL_TAXONOMY:
            self.session.add(
                BusinessOntologyType(
                    concept_category=seed.concept_category,
                    type_code=seed.type_code,
                    type_label=seed.type_label,
                    description=seed.description,
                    is_active=True,
                    sort_order=seed.sort_order,
                    created_at=now,
                    updated_at=now,
                )
            )
        self.session.flush()
        return len(INITIAL_TAXONOMY)

    def seed_rules_if_empty(self, *, now: datetime) -> int:
        if self.count_rules() > 0:
            return 0
        type_map = self.get_type_code_map()
        inserted = 0
        for seed in build_rule_seeds():
            target_id = type_map.get((seed.concept_category, seed.target_type_code))
            if target_id is None:
                continue
            self.session.add(
                BusinessOntologyRule(
                    rule_code=seed.rule_code,
                    concept_category=seed.concept_category,
                    target_type_id=target_id,
                    priority=seed.priority,
                    conditions_json=seed.conditions_json,
                    description=seed.description,
                    score_weight=seed.score_weight,
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                )
            )
            inserted += 1
        self.session.flush()
        return inserted

    def get_type_code_map(self) -> dict[tuple[str, str], int]:
        rows = self.session.scalars(select(BusinessOntologyType)).all()
        return {(row.concept_category, row.type_code): int(row.type_id) for row in rows}

    def list_types(self, *, concept_category: str | None = None) -> list[BusinessOntologyType]:
        query = select(BusinessOntologyType).where(BusinessOntologyType.is_active.is_(True))
        if concept_category:
            query = query.where(BusinessOntologyType.concept_category == concept_category)
        query = query.order_by(BusinessOntologyType.concept_category, BusinessOntologyType.sort_order)
        return list(self.session.scalars(query).all())

    def fetch_active_rules(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    bor.rule_code,
                    bor.concept_category,
                    bot.type_code,
                    bor.conditions_json,
                    bor.score_weight,
                    bor.target_type_id
                FROM business_ontology_rule bor
                INNER JOIN business_ontology_type bot ON bot.type_id = bor.target_type_id
                WHERE bor.is_active = TRUE AND bot.is_active = TRUE
                ORDER BY bor.priority ASC, bor.rule_id ASC
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def fetch_entity_contexts(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    cbe.canonical_id,
                    cbe.canonical_name,
                    cbe.primary_rfc,
                    cbe.normalized_name,
                    cbe.alias_count,
                    COALESCE(bep.total_movements, 0) AS total_movements,
                    COALESCE(bep.total_amount, 0) AS total_amount,
                    COALESCE(bep.debit_amount, 0) AS debit_amount,
                    COALESCE(bep.credit_amount, 0) AS credit_amount,
                    bep.debit_credit_ratio,
                    COALESCE(bep.related_accounts_count, 0) AS related_accounts_count,
                    COALESCE(bep.related_counterparties_count, 0) AS related_counterparties_count,
                    COALESCE(bep.active_months, 0) AS active_months,
                    COALESCE(bep.dimensions_used, '[]'::jsonb) AS dimensions_used,
                    COALESCE(bep.top_accounts, '[]'::jsonb) AS top_accounts,
                    COALESCE(bep.top_counterparties, '[]'::jsonb) AS top_counterparties,
                    COALESCE(bep.currencies, '[]'::jsonb) AS currencies,
                    COALESCE(bep.profile_completeness, 0) AS profile_completeness
                FROM canonical_business_entity cbe
                LEFT JOIN business_entity_profile bep ON bep.canonical_id = cbe.canonical_id
                ORDER BY cbe.canonical_id
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def upsert_assignment(
        self,
        *,
        canonical_id: int,
        concept_category: str,
        type_id: int,
        rule_code: str,
        evidence_json: dict,
        score: Decimal,
        confidence: Decimal,
        now: datetime,
    ) -> bool:
        existing = self.session.scalar(
            select(BusinessOntologyAssignment).where(
                BusinessOntologyAssignment.canonical_id == canonical_id,
                BusinessOntologyAssignment.concept_category == concept_category,
                BusinessOntologyAssignment.type_id == type_id,
                BusinessOntologyAssignment.rule_code == rule_code,
            )
        )
        if existing is None:
            self.session.add(
                BusinessOntologyAssignment(
                    canonical_id=canonical_id,
                    concept_category=concept_category,
                    type_id=type_id,
                    rule_code=rule_code,
                    evidence_json=evidence_json,
                    score=score,
                    confidence=confidence,
                    status=STATUS_PENDING,
                    created_at=now,
                    updated_at=now,
                )
            )
            return True
        if existing.status != STATUS_PENDING:
            return False
        if score > existing.score:
            existing.score = score
        if confidence > existing.confidence:
            existing.confidence = confidence
        existing.evidence_json = evidence_json
        existing.updated_at = now
        return False

    def list_ontology_entities(
        self,
        *,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[int], int]:
        conditions = ["1=1"]
        params: dict = {"limit": page_size, "offset": (page - 1) * page_size}
        if search:
            conditions.append(
                "(cbe.canonical_name ILIKE :search OR cbe.normalized_name ILIKE :search)"
            )
            params["search"] = f"%{search.strip()}%"
        where_clause = " AND ".join(conditions)
        total = self.session.execute(
            text(f"SELECT COUNT(*) FROM canonical_business_entity cbe WHERE {where_clause}"),
            params,
        ).scalar_one()
        rows = self.session.execute(
            text(
                f"""
                SELECT cbe.canonical_id
                FROM canonical_business_entity cbe
                WHERE {where_clause}
                ORDER BY cbe.canonical_id
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).fetchall()
        return [int(row[0]) for row in rows], int(total)

    def fetch_assignments_for_canonical(self, canonical_id: int) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    boa.*,
                    bot.type_code,
                    bot.type_label
                FROM business_ontology_assignment boa
                INNER JOIN business_ontology_type bot ON bot.type_id = boa.type_id
                WHERE boa.canonical_id = :canonical_id
                ORDER BY boa.confidence DESC, boa.score DESC, boa.assignment_id ASC
                """
            ),
            {"canonical_id": canonical_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def list_assignments(
        self,
        *,
        status: str | None = STATUS_PENDING,
        concept_category: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict], int]:
        conditions = ["1=1"]
        params: dict = {"limit": page_size, "offset": (page - 1) * page_size}
        if status:
            conditions.append("boa.status = :status")
            params["status"] = status
        if concept_category:
            conditions.append("boa.concept_category = :concept_category")
            params["concept_category"] = concept_category
        where_clause = " AND ".join(conditions)
        total = self.session.execute(
            text(f"SELECT COUNT(*) FROM business_ontology_assignment boa WHERE {where_clause}"),
            params,
        ).scalar_one()
        rows = self.session.execute(
            text(
                f"""
                SELECT boa.*, bot.type_code, bot.type_label, cbe.canonical_name
                FROM business_ontology_assignment boa
                INNER JOIN business_ontology_type bot ON bot.type_id = boa.type_id
                INNER JOIN canonical_business_entity cbe ON cbe.canonical_id = boa.canonical_id
                WHERE {where_clause}
                ORDER BY boa.confidence DESC, boa.score DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()
        return [dict(row) for row in rows], int(total)

    def get_canonical_identity(self, canonical_id: int) -> dict | None:
        row = self.session.execute(
            text(
                """
                SELECT canonical_id, canonical_name, primary_rfc, normalized_name, alias_count
                FROM canonical_business_entity
                WHERE canonical_id = :canonical_id
                """
            ),
            {"canonical_id": canonical_id},
        ).mappings().first()
        return dict(row) if row else None

    def get_profile_summary(self, canonical_id: int) -> dict | None:
        row = self.session.scalar(
            select(BusinessEntityProfile).where(BusinessEntityProfile.canonical_id == canonical_id)
        )
        if row is None:
            return None
        return {
            "total_movements": int(row.total_movements),
            "total_amount": row.total_amount,
            "debit_credit_ratio": row.debit_credit_ratio,
            "dimensions_used": list(row.dimensions_used or []),
            "profile_completeness": row.profile_completeness,
        }

    def find_health_issues(self) -> dict[str, list[dict]]:
        entities_without = self.session.execute(
            text(
                """
                SELECT cbe.canonical_id, cbe.canonical_name
                FROM canonical_business_entity cbe
                LEFT JOIN business_ontology_assignment boa ON boa.canonical_id = cbe.canonical_id
                WHERE boa.assignment_id IS NULL
                LIMIT 100
                """
            )
        ).mappings().all()

        invalid_scores = self.session.execute(
            text(
                """
                SELECT assignment_id, canonical_id, score, confidence
                FROM business_ontology_assignment
                WHERE score < 0 OR score > 1 OR confidence < 0 OR confidence > 1
                LIMIT 100
                """
            )
        ).mappings().all()

        incomplete_relations = self.session.execute(
            text(
                """
                SELECT boa.assignment_id, boa.canonical_id, boa.rule_code
                FROM business_ontology_assignment boa
                LEFT JOIN business_entity_profile bep ON bep.canonical_id = boa.canonical_id
                WHERE bep.profile_id IS NULL AND boa.concept_category IN ('nature', 'behavior')
                LIMIT 100
                """
            )
        ).mappings().all()

        contradictory = self.session.execute(
            text(
                """
                SELECT canonical_id, concept_category, COUNT(DISTINCT type_id) AS type_count
                FROM business_ontology_assignment
                WHERE status = 'pending'
                  AND concept_category = 'role'
                GROUP BY canonical_id, concept_category
                HAVING COUNT(DISTINCT type_id) > 2
                LIMIT 100
                """
            )
        ).mappings().all()

        incompatible_natures = self.session.execute(
            text(
                """
                SELECT boa.canonical_id, COUNT(DISTINCT boa.type_id) AS nature_count
                FROM business_ontology_assignment boa
                INNER JOIN business_ontology_type bot ON bot.type_id = boa.type_id
                WHERE boa.concept_category = :nature
                  AND boa.status = 'pending'
                  AND bot.type_code NOT IN ('OTRO', 'AJUSTE')
                GROUP BY boa.canonical_id
                HAVING COUNT(DISTINCT boa.type_id) > 1
                LIMIT 100
                """
            ),
            {"nature": CONCEPT_NATURE},
        ).mappings().all()

        return {
            "entities_without_suggestions": [dict(row) for row in entities_without],
            "invalid_scores": [dict(row) for row in invalid_scores],
            "incomplete_relations": [dict(row) for row in incomplete_relations],
            "contradictory_rules": [dict(row) for row in contradictory],
            "incompatible_natures": [dict(row) for row in incompatible_natures],
        }
