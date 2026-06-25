from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.canonical_business_entity.constants import (
    COMMERCIAL_SOURCE_COLUMNS,
    SORTABLE_CANONICAL_FIELDS,
    SUGGESTION_PENDING,
)
from app.canonical_business_entity.matcher import EntityRecord
from app.canonical_business_entity.normalizer import extract_rfc, normalize_organization_name
from app.models.business_entity_master import BusinessEntityMaster
from app.models.canonical_business_entity import (
    BusinessEntityResolution,
    CanonicalBusinessEntity,
    CanonicalEntitySuggestion,
)


class CanonicalBusinessEntityRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_canonical(self) -> int:
        return self.session.scalar(select(func.count()).select_from(CanonicalBusinessEntity)) or 0

    def count_commercial_entities(self) -> int:
        return (
            self.session.scalar(
                select(func.count())
                .select_from(BusinessEntityMaster)
                .where(BusinessEntityMaster.source_column.in_(COMMERCIAL_SOURCE_COLUMNS))
            )
            or 0
        )

    def count_resolved_commercial(self) -> int:
        row = self.session.execute(
            text(
                """
                SELECT COUNT(*) AS resolved
                FROM business_entity_resolution ber
                INNER JOIN business_entity_master bem ON bem.entity_id = ber.entity_id
                WHERE bem.source_column IN ('cuenta_proveedor', 'cuenta_cliente')
                """
            )
        ).mappings().one()
        return int(row["resolved"])

    def count_canonical_matches(self) -> int:
        row = self.session.execute(
            text(
                """
                SELECT COUNT(*) AS matched
                FROM (
                    SELECT canonical_id
                    FROM business_entity_resolution
                    GROUP BY canonical_id
                    HAVING COUNT(*) > 1
                ) grouped
                """
            )
        ).mappings().one()
        return int(row["matched"])

    def count_pending_suggestions(self) -> int:
        return (
            self.session.scalar(
                select(func.count())
                .select_from(CanonicalEntitySuggestion)
                .where(CanonicalEntitySuggestion.status == SUGGESTION_PENDING)
            )
            or 0
        )

    def count_automatic_suggestions(self) -> int:
        return self.session.scalar(select(func.count()).select_from(CanonicalEntitySuggestion)) or 0

    def fetch_commercial_entities(self) -> list[EntityRecord]:
        rows = self.session.scalars(
            select(BusinessEntityMaster)
            .where(BusinessEntityMaster.source_column.in_(COMMERCIAL_SOURCE_COLUMNS))
            .order_by(BusinessEntityMaster.entity_id)
        ).all()
        return [
            EntityRecord(
                entity_id=int(row.entity_id),
                entity_code=row.entity_code,
                entity_name=row.entity_name,
                source_column=row.source_column,
            )
            for row in rows
        ]

    def get_unresolved_commercial_entity_ids(self) -> list[int]:
        rows = self.session.execute(
            text(
                """
                SELECT bem.entity_id
                FROM business_entity_master bem
                LEFT JOIN business_entity_resolution ber ON ber.entity_id = bem.entity_id
                WHERE bem.source_column IN ('cuenta_proveedor', 'cuenta_cliente')
                  AND ber.entity_id IS NULL
                ORDER BY bem.entity_id
                """
            )
        ).fetchall()
        return [int(row[0]) for row in rows]

    def create_singleton_canonical(
        self,
        entity: BusinessEntityMaster,
        *,
        now: datetime,
    ) -> tuple[CanonicalBusinessEntity, BusinessEntityResolution]:
        normalized = normalize_organization_name(entity.entity_name)
        rfc = extract_rfc(entity.entity_code, entity.entity_name)
        canonical = CanonicalBusinessEntity(
            canonical_name=entity.entity_name,
            normalized_name=normalized or entity.entity_code,
            primary_rfc=rfc,
            alias_count=1,
            created_at=now,
            updated_at=now,
        )
        self.session.add(canonical)
        self.session.flush()
        resolution = BusinessEntityResolution(
            entity_id=entity.entity_id,
            canonical_id=canonical.canonical_id,
            resolution_rule="singleton_bootstrap",
            resolution_score=Decimal("1.0000"),
            created_at=now,
            updated_at=now,
        )
        self.session.add(resolution)
        return canonical, resolution

    def upsert_suggestion(
        self,
        *,
        source_entity_id: int,
        candidate_entity_id: int,
        rule_used: str,
        score: Decimal,
        now: datetime,
    ) -> bool:
        existing = self.session.scalar(
            select(CanonicalEntitySuggestion).where(
                CanonicalEntitySuggestion.source_entity_id == source_entity_id,
                CanonicalEntitySuggestion.candidate_entity_id == candidate_entity_id,
                CanonicalEntitySuggestion.rule_used == rule_used,
            )
        )
        if existing is None:
            self.session.add(
                CanonicalEntitySuggestion(
                    source_entity_id=source_entity_id,
                    candidate_entity_id=candidate_entity_id,
                    rule_used=rule_used,
                    score=score,
                    status=SUGGESTION_PENDING,
                    created_at=now,
                    updated_at=now,
                )
            )
            return True
        if score > existing.score:
            existing.score = score
        existing.updated_at = now
        return False

    def list_canonical(
        self,
        *,
        search: str | None = None,
        sort_by: str = "alias_count",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[CanonicalBusinessEntity], int]:
        query = select(CanonicalBusinessEntity)
        count_query = select(func.count()).select_from(CanonicalBusinessEntity)
        if search:
            pattern = f"%{search.strip()}%"
            condition = or_(
                CanonicalBusinessEntity.canonical_name.ilike(pattern),
                CanonicalBusinessEntity.normalized_name.ilike(pattern),
                CanonicalBusinessEntity.primary_rfc.ilike(pattern),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)

        sort_field = sort_by if sort_by in SORTABLE_CANONICAL_FIELDS else "alias_count"
        sort_column = getattr(CanonicalBusinessEntity, sort_field)
        order = sort_column.desc() if sort_dir.lower() == "desc" else sort_column.asc()
        query = query.order_by(order, CanonicalBusinessEntity.canonical_id.asc())

        total = self.session.scalar(count_query) or 0
        rows = self.session.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
        return list(rows), int(total)

    def list_aliases_for_canonical(self, canonical_id: int) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    bem.entity_id,
                    bem.entity_code,
                    bem.entity_name,
                    bem.source_column,
                    ber.resolution_rule,
                    ber.resolution_score
                FROM business_entity_resolution ber
                INNER JOIN business_entity_master bem ON bem.entity_id = ber.entity_id
                WHERE ber.canonical_id = :canonical_id
                ORDER BY bem.movement_count DESC, bem.entity_code ASC
                """
            ),
            {"canonical_id": canonical_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def list_suggestions(
        self,
        *,
        status: str | None = SUGGESTION_PENDING,
        min_score: float | None = None,
        page: int = 1,
        page_size: int = 50,
        sort_dir: str = "desc",
    ) -> tuple[list[dict], int]:
        conditions = ["1=1"]
        params: dict = {"limit": page_size, "offset": (page - 1) * page_size}
        if status:
            conditions.append("ces.status = :status")
            params["status"] = status
        if min_score is not None:
            conditions.append("ces.score >= :min_score")
            params["min_score"] = min_score
        where_clause = " AND ".join(conditions)
        order = "DESC" if sort_dir.lower() == "desc" else "ASC"

        total = self.session.execute(
            text(f"SELECT COUNT(*) FROM canonical_entity_suggestion ces WHERE {where_clause}"),
            params,
        ).scalar_one()

        rows = self.session.execute(
            text(
                f"""
                SELECT
                    ces.suggestion_id,
                    ces.rule_used,
                    ces.score,
                    ces.status,
                    ces.created_at,
                    src.entity_id AS source_entity_id,
                    src.entity_code AS source_entity_code,
                    src.entity_name AS source_entity_name,
                    src.source_column AS source_source_column,
                    cand.entity_id AS candidate_entity_id,
                    cand.entity_code AS candidate_entity_code,
                    cand.entity_name AS candidate_entity_name,
                    cand.source_column AS candidate_source_column
                FROM canonical_entity_suggestion ces
                INNER JOIN business_entity_master src ON src.entity_id = ces.source_entity_id
                INNER JOIN business_entity_master cand ON cand.entity_id = ces.candidate_entity_id
                WHERE {where_clause}
                ORDER BY ces.score {order}, ces.suggestion_id ASC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()
        return [dict(row) for row in rows], int(total)

    def find_health_issues(self) -> dict[str, list[dict]]:
        orphans = self.session.execute(
            text(
                """
                SELECT bem.entity_id, bem.entity_code, bem.entity_name
                FROM business_entity_master bem
                LEFT JOIN business_entity_resolution ber ON ber.entity_id = bem.entity_id
                WHERE bem.source_column IN ('cuenta_proveedor', 'cuenta_cliente')
                  AND ber.entity_id IS NULL
                ORDER BY bem.entity_id
                LIMIT 100
                """
            )
        ).mappings().all()

        duplicate_resolutions = self.session.execute(
            text(
                """
                SELECT entity_id, COUNT(*) AS occurrences
                FROM business_entity_resolution
                GROUP BY entity_id
                HAVING COUNT(*) > 1
                LIMIT 100
                """
            )
        ).mappings().all()

        invalid_scores = self.session.execute(
            text(
                """
                SELECT suggestion_id, score
                FROM canonical_entity_suggestion
                WHERE score < 0 OR score > 1
                LIMIT 100
                """
            )
        ).mappings().all()

        invalid_resolution_scores = self.session.execute(
            text(
                """
                SELECT resolution_id, resolution_score
                FROM business_entity_resolution
                WHERE resolution_score < 0 OR resolution_score > 1
                LIMIT 100
                """
            )
        ).mappings().all()

        return {
            "orphan_entities": [dict(row) for row in orphans],
            "duplicate_resolutions": [dict(row) for row in duplicate_resolutions],
            "invalid_suggestion_scores": [dict(row) for row in invalid_scores],
            "invalid_resolution_scores": [dict(row) for row in invalid_resolution_scores],
        }
