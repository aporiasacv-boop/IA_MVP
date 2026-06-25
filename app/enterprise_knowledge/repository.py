import time
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.enterprise_knowledge.constants import EKO_SCHEMA_ID, EKO_VERSION, REQUIRED_SECTIONS, SORTABLE_KNOWLEDGE_FIELDS
from app.enterprise_knowledge.knowledge_builder import build_enterprise_knowledge_object, eko_to_payload
from app.enterprise_knowledge.schemas import EnterpriseKnowledgeObjectSchema
from app.models.enterprise_knowledge_object import EnterpriseKnowledgeObject


class EnterpriseKnowledgeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_objects(self) -> int:
        return self.session.scalar(select(func.count()).select_from(EnterpriseKnowledgeObject)) or 0

    def count_canonical(self) -> int:
        row = self.session.execute(text("SELECT COUNT(*) FROM canonical_business_entity")).scalar_one()
        return int(row)

    def count_incomplete(self, *, threshold: float = 0.5) -> int:
        return (
            self.session.scalar(
                select(func.count())
                .select_from(EnterpriseKnowledgeObject)
                .where(EnterpriseKnowledgeObject.completeness < threshold)
            )
            or 0
        )

    def average_completeness(self) -> float:
        value = self.session.scalar(select(func.avg(EnterpriseKnowledgeObject.completeness)))
        return round(float(value or 0), 4)

    def average_confidence(self) -> float:
        value = self.session.scalar(select(func.avg(EnterpriseKnowledgeObject.average_confidence)))
        return round(float(value or 0), 4)

    def get_last_refresh(self) -> datetime | None:
        return self.session.scalar(select(func.max(EnterpriseKnowledgeObject.built_at)))

    def fetch_build_contexts(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT cbe.canonical_id, cbe.canonical_name, cbe.normalized_name,
                       cbe.primary_rfc, cbe.alias_count
                FROM canonical_business_entity cbe
                ORDER BY cbe.canonical_id
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def fetch_aliases(self, canonical_id: int) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT bem.entity_id, bem.entity_code, bem.entity_name, bem.source_column,
                       ber.resolution_rule, ber.resolution_score
                FROM business_entity_resolution ber
                INNER JOIN business_entity_master bem ON bem.entity_id = ber.entity_id
                WHERE ber.canonical_id = :canonical_id
                ORDER BY bem.movement_count DESC
                """
            ),
            {"canonical_id": canonical_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def fetch_profile(self, canonical_id: int) -> dict | None:
        row = self.session.execute(
            text("SELECT * FROM business_entity_profile WHERE canonical_id = :canonical_id"),
            {"canonical_id": canonical_id},
        ).mappings().first()
        return dict(row) if row else None

    def fetch_ontology_assignments(self, canonical_id: int) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT boa.assignment_id, boa.concept_category, boa.rule_code,
                       boa.evidence_json, boa.score, boa.confidence, boa.status,
                       bot.type_code, bot.type_label
                FROM business_ontology_assignment boa
                INNER JOIN business_ontology_type bot ON bot.type_id = boa.type_id
                WHERE boa.canonical_id = :canonical_id
                ORDER BY boa.confidence DESC
                """
            ),
            {"canonical_id": canonical_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def upsert_object(
        self,
        *,
        canonical_id: int,
        payload: dict,
        completeness: Decimal,
        average_confidence: Decimal,
        built_at: datetime,
    ) -> tuple[EnterpriseKnowledgeObject, bool]:
        existing = self.session.scalar(
            select(EnterpriseKnowledgeObject).where(EnterpriseKnowledgeObject.canonical_id == canonical_id)
        )
        is_new = existing is None
        obj = existing or EnterpriseKnowledgeObject(canonical_id=canonical_id, created_at=built_at)
        obj.knowledge_payload = payload
        obj.completeness = completeness
        obj.average_confidence = average_confidence
        obj.built_at = built_at
        obj.updated_at = built_at
        if is_new:
            self.session.add(obj)
        return obj, is_new

    def get_object_by_canonical_id(self, canonical_id: int) -> EnterpriseKnowledgeObject | None:
        return self.session.scalar(
            select(EnterpriseKnowledgeObject).where(EnterpriseKnowledgeObject.canonical_id == canonical_id)
        )

    def list_objects(
        self,
        *,
        search: str | None = None,
        sort_by: str = "completeness",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict], int]:
        conditions = ["1=1"]
        params: dict = {"limit": page_size, "offset": (page - 1) * page_size}
        if search:
            conditions.append("(cbe.canonical_name ILIKE :search OR cbe.normalized_name ILIKE :search)")
            params["search"] = f"%{search.strip()}%"
        where_clause = " AND ".join(conditions)
        sort_field = "eko.completeness" if sort_by == "completeness" else (
            "eko.average_confidence" if sort_by == "average_confidence" else (
                "eko.built_at" if sort_by == "built_at" else "cbe.canonical_name"
            )
        )
        order = "DESC" if sort_dir.lower() == "desc" else "ASC"
        if sort_by not in SORTABLE_KNOWLEDGE_FIELDS:
            sort_field = "eko.completeness"

        total = self.session.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM enterprise_knowledge_object eko
                INNER JOIN canonical_business_entity cbe ON cbe.canonical_id = eko.canonical_id
                WHERE {where_clause}
                """
            ),
            params,
        ).scalar_one()

        rows = self.session.execute(
            text(
                f"""
                SELECT eko.knowledge_id, eko.canonical_id, cbe.canonical_name,
                       eko.completeness, eko.average_confidence, eko.built_at
                FROM enterprise_knowledge_object eko
                INNER JOIN canonical_business_entity cbe ON cbe.canonical_id = eko.canonical_id
                WHERE {where_clause}
                ORDER BY {sort_field} {order}, eko.canonical_id ASC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()
        return [dict(row) for row in rows], int(total)

    def find_health_issues(self) -> dict[str, list[dict]]:
        incomplete = self.session.execute(
            text(
                """
                SELECT knowledge_id, canonical_id, completeness
                FROM enterprise_knowledge_object
                WHERE completeness < 0.3
                LIMIT 100
                """
            )
        ).mappings().all()

        invalid_confidence = self.session.execute(
            text(
                """
                SELECT knowledge_id, canonical_id, average_confidence
                FROM enterprise_knowledge_object
                WHERE average_confidence < 0 OR average_confidence > 1
                LIMIT 100
                """
            )
        ).mappings().all()

        missing_evidence = self.session.execute(
            text(
                """
                SELECT knowledge_id, canonical_id
                FROM enterprise_knowledge_object
                WHERE knowledge_payload->'evidence' = '[]'::jsonb
                   OR jsonb_array_length(COALESCE(knowledge_payload->'evidence', '[]'::jsonb)) = 0
                LIMIT 100
                """
            )
        ).mappings().all()

        empty_sections = self.session.execute(
            text(
                """
                SELECT knowledge_id, canonical_id
                FROM enterprise_knowledge_object
                WHERE jsonb_array_length(COALESCE(knowledge_payload->'facts', '[]'::jsonb)) = 0
                  AND jsonb_array_length(COALESCE(knowledge_payload->'identity'->'items', '[]'::jsonb)) = 0
                LIMIT 100
                """
            )
        ).mappings().all()

        broken_relationships = self.session.execute(
            text(
                """
                SELECT eko.knowledge_id, eko.canonical_id
                FROM enterprise_knowledge_object eko
                LEFT JOIN business_entity_profile bep ON bep.canonical_id = eko.canonical_id
                WHERE jsonb_array_length(COALESCE(eko.knowledge_payload->'relationships', '[]'::jsonb)) > 0
                  AND bep.profile_id IS NULL
                LIMIT 100
                """
            )
        ).mappings().all()

        contradictory = self.session.execute(
            text(
                """
                SELECT knowledge_id, canonical_id
                FROM enterprise_knowledge_object
                WHERE EXISTS (
                    SELECT 1 FROM jsonb_array_elements(knowledge_payload->'alerts') elem
                    WHERE elem->>'key' = 'conflicting_natures'
                )
                LIMIT 100
                """
            )
        ).mappings().all()

        return {
            "incomplete_objects": [dict(row) for row in incomplete],
            "invalid_confidence": [dict(row) for row in invalid_confidence],
            "missing_evidence": [dict(row) for row in missing_evidence],
            "empty_sections": [dict(row) for row in empty_sections],
            "broken_relationships": [dict(row) for row in broken_relationships],
            "contradictory_facts": [dict(row) for row in contradictory],
        }


class KnowledgeBuildEngine:
    def __init__(self, repository: EnterpriseKnowledgeRepository) -> None:
        self._repository = repository

    def run_idempotent(self, *, now: datetime | None = None) -> dict:
        started = time.perf_counter()
        timestamp = now or datetime.now()
        created = 0
        updated = 0
        processed = 0

        for canonical in self._repository.fetch_build_contexts():
            canonical_id = int(canonical["canonical_id"])
            aliases = self._repository.fetch_aliases(canonical_id)
            profile = self._repository.fetch_profile(canonical_id)
            assignments = self._repository.fetch_ontology_assignments(canonical_id)

            eko = build_enterprise_knowledge_object(
                canonical=canonical,
                aliases=aliases,
                profile=profile,
                ontology_assignments=assignments,
                computed_at=timestamp,
            )
            payload = eko_to_payload(eko)
            _, is_new = self._repository.upsert_object(
                canonical_id=canonical_id,
                payload=payload,
                completeness=eko.quality.completeness,
                average_confidence=eko.quality.average_confidence,
                built_at=timestamp,
            )
            processed += 1
            if is_new:
                created += 1
            else:
                updated += 1

        self._repository.session.commit()
        elapsed = round(time.perf_counter() - started, 4)
        return {
            "objects_upserted": created + updated,
            "objects_created": created,
            "objects_updated": updated,
            "entities_processed": processed,
            "build_time_seconds": elapsed,
        }
