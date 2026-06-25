import time
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.enterprise_knowledge.schemas import EnterpriseKnowledgeObjectSchema
from app.enterprise_reasoning.constants import SORTABLE_REASONING_FIELDS
from app.enterprise_reasoning.reasoning_builder import build_enterprise_reasoning_object, ero_to_payload
from app.enterprise_reasoning.schemas import EnterpriseReasoningObjectSchema
from app.models.enterprise_reasoning_object import EnterpriseReasoningObject


class EnterpriseReasoningRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_objects(self) -> int:
        return self.session.scalar(select(func.count()).select_from(EnterpriseReasoningObject)) or 0

    def count_knowledge_objects(self) -> int:
        row = self.session.execute(text("SELECT COUNT(*) FROM enterprise_knowledge_object")).scalar_one()
        return int(row)

    def count_incomplete(self, *, threshold: int = 1) -> int:
        return (
            self.session.scalar(
                select(func.count())
                .select_from(EnterpriseReasoningObject)
                .where(EnterpriseReasoningObject.findings_count < threshold)
            )
            or 0
        )

    def average_confidence(self) -> float:
        value = self.session.scalar(select(func.avg(EnterpriseReasoningObject.average_confidence)))
        return round(float(value or 0), 4)

    def average_findings(self) -> float:
        value = self.session.scalar(select(func.avg(EnterpriseReasoningObject.findings_count)))
        return round(float(value or 0), 4)

    def average_alerts(self) -> float:
        value = self.session.scalar(select(func.avg(EnterpriseReasoningObject.alerts_count)))
        return round(float(value or 0), 4)

    def average_recommendations(self) -> float:
        value = self.session.scalar(select(func.avg(EnterpriseReasoningObject.recommendations_count)))
        return round(float(value or 0), 4)

    def get_last_refresh(self) -> datetime | None:
        return self.session.scalar(select(func.max(EnterpriseReasoningObject.built_at)))

    def fetch_eko_payloads(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT eko.canonical_id, eko.knowledge_payload, cbe.canonical_name
                FROM enterprise_knowledge_object eko
                INNER JOIN canonical_business_entity cbe ON cbe.canonical_id = eko.canonical_id
                ORDER BY eko.canonical_id
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def upsert_object(
        self,
        *,
        canonical_id: int,
        payload: dict,
        average_confidence: Decimal,
        findings_count: int,
        alerts_count: int,
        recommendations_count: int,
        built_at: datetime,
    ) -> tuple[EnterpriseReasoningObject, bool]:
        existing = self.session.scalar(
            select(EnterpriseReasoningObject).where(EnterpriseReasoningObject.canonical_id == canonical_id)
        )
        is_new = existing is None
        obj = existing or EnterpriseReasoningObject(canonical_id=canonical_id, created_at=built_at)
        obj.reasoning_payload = payload
        obj.average_confidence = average_confidence
        obj.findings_count = findings_count
        obj.alerts_count = alerts_count
        obj.recommendations_count = recommendations_count
        obj.built_at = built_at
        obj.updated_at = built_at
        if is_new:
            self.session.add(obj)
        return obj, is_new

    def get_object_by_canonical_id(self, canonical_id: int) -> EnterpriseReasoningObject | None:
        return self.session.scalar(
            select(EnterpriseReasoningObject).where(EnterpriseReasoningObject.canonical_id == canonical_id)
        )

    def list_objects(
        self,
        *,
        search: str | None = None,
        sort_by: str = "average_confidence",
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
        sort_field = "ero.average_confidence" if sort_by == "average_confidence" else (
            "ero.built_at" if sort_by == "built_at" else (
                "ero.findings_count" if sort_by == "findings_count" else "cbe.canonical_name"
            )
        )
        order = "DESC" if sort_dir.lower() == "desc" else "ASC"
        if sort_by not in SORTABLE_REASONING_FIELDS:
            sort_field = "ero.average_confidence"

        total = self.session.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM enterprise_reasoning_object ero
                INNER JOIN canonical_business_entity cbe ON cbe.canonical_id = ero.canonical_id
                WHERE {where_clause}
                """
            ),
            params,
        ).scalar_one()

        rows = self.session.execute(
            text(
                f"""
                SELECT ero.reasoning_id, ero.canonical_id, cbe.canonical_name,
                       ero.average_confidence, ero.findings_count, ero.alerts_count,
                       ero.recommendations_count, ero.built_at
                FROM enterprise_reasoning_object ero
                INNER JOIN canonical_business_entity cbe ON cbe.canonical_id = ero.canonical_id
                WHERE {where_clause}
                ORDER BY {sort_field} {order}, ero.canonical_id ASC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()
        return [dict(row) for row in rows], int(total)

    def find_health_issues(self) -> dict[str, list[dict]]:
        missing_evidence = self.session.execute(
            text(
                """
                SELECT reasoning_id, canonical_id
                FROM enterprise_reasoning_object
                WHERE jsonb_array_length(COALESCE(reasoning_payload->'evidence', '[]'::jsonb)) = 0
                LIMIT 100
                """
            )
        ).mappings().all()

        invalid_confidence = self.session.execute(
            text(
                """
                SELECT reasoning_id, canonical_id, average_confidence
                FROM enterprise_reasoning_object
                WHERE average_confidence < 0 OR average_confidence > 1
                LIMIT 100
                """
            )
        ).mappings().all()

        incomplete = self.session.execute(
            text(
                """
                SELECT reasoning_id, canonical_id
                FROM enterprise_reasoning_object
                WHERE findings_count = 0 AND alerts_count = 0 AND recommendations_count = 0
                LIMIT 100
                """
            )
        ).mappings().all()

        duplicate_findings = self.session.execute(
            text(
                """
                SELECT ero.reasoning_id, ero.canonical_id
                FROM enterprise_reasoning_object ero
                WHERE EXISTS (
                    SELECT 1
                    FROM (
                        SELECT elem->>'key' AS item_key, COUNT(*) AS cnt
                        FROM jsonb_array_elements(ero.reasoning_payload->'findings') elem
                        GROUP BY elem->>'key'
                        HAVING COUNT(*) > 1
                    ) dup
                )
                LIMIT 100
                """
            )
        ).mappings().all()

        contradictory = self.session.execute(
            text(
                """
                SELECT reasoning_id, canonical_id
                FROM enterprise_reasoning_object
                WHERE jsonb_array_length(COALESCE(reasoning_payload->'risks', '[]'::jsonb)) > 0
                  AND jsonb_array_length(COALESCE(reasoning_payload->'opportunities', '[]'::jsonb)) > 0
                  AND EXISTS (
                    SELECT 1 FROM jsonb_array_elements(reasoning_payload->'risks') r
                    JOIN jsonb_array_elements(reasoning_payload->'opportunities') o ON r->>'key' = o->>'key'
                  )
                LIMIT 100
                """
            )
        ).mappings().all()

        incompatible_recommendations = self.session.execute(
            text(
                """
                SELECT reasoning_id, canonical_id
                FROM enterprise_reasoning_object
                WHERE (
                    SELECT COUNT(DISTINCT elem->>'rule_code')
                    FROM jsonb_array_elements(reasoning_payload->'recommendations') elem
                ) < (
                    SELECT COUNT(*)
                    FROM jsonb_array_elements(reasoning_payload->'recommendations') elem
                )
                LIMIT 100
                """
            )
        ).mappings().all()

        return {
            "missing_evidence": [dict(row) for row in missing_evidence],
            "invalid_confidence": [dict(row) for row in invalid_confidence],
            "incomplete_objects": [dict(row) for row in incomplete],
            "duplicate_findings": [dict(row) for row in duplicate_findings],
            "contradictory_rules": [dict(row) for row in contradictory],
            "incompatible_recommendations": [dict(row) for row in incompatible_recommendations],
        }


class ReasoningBuildEngine:
    def __init__(self, repository: EnterpriseReasoningRepository) -> None:
        self._repository = repository

    def run_idempotent(self, *, now: datetime | None = None) -> dict:
        started = time.perf_counter()
        timestamp = now or datetime.now()
        created = 0
        updated = 0
        processed = 0
        total_rules_executed = 0

        for row in self._repository.fetch_eko_payloads():
            canonical_id = int(row["canonical_id"])
            eko = EnterpriseKnowledgeObjectSchema.model_validate(row["knowledge_payload"])
            ero, rules_executed = build_enterprise_reasoning_object(eko=eko, computed_at=timestamp)
            total_rules_executed += rules_executed
            payload = ero_to_payload(ero)
            _, is_new = self._repository.upsert_object(
                canonical_id=canonical_id,
                payload=payload,
                average_confidence=ero.confidence.average_confidence,
                findings_count=len(ero.findings),
                alerts_count=len(ero.alerts),
                recommendations_count=len(ero.recommendations),
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
            "rules_executed": total_rules_executed,
            "build_time_seconds": elapsed,
        }
