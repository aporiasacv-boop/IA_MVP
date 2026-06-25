from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.business_entity_master.constants import SORTABLE_FIELDS
from app.models.business_entity_master import BusinessEntityMaster


class BusinessEntityMasterRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_all(self) -> int:
        return self.session.scalar(select(func.count()).select_from(BusinessEntityMaster)) or 0

    def count_duplicated_codes(self) -> int:
        row = self.session.execute(
            text(
                """
                SELECT COUNT(*) AS duplicated
                FROM (
                    SELECT entity_code
                    FROM business_entity_master
                    GROUP BY entity_code
                    HAVING COUNT(*) > 1
                ) dup
                """
            )
        ).mappings().one()
        return int(row["duplicated"])

    def list_entities(
        self,
        *,
        search: str | None = None,
        source_column: str | None = None,
        classification_status: str | None = None,
        sort_by: str = "movement_count",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[BusinessEntityMaster], int]:
        query = select(BusinessEntityMaster)
        count_query = select(func.count()).select_from(BusinessEntityMaster)

        if search:
            pattern = f"%{search.strip()}%"
            condition = or_(
                BusinessEntityMaster.entity_code.ilike(pattern),
                BusinessEntityMaster.entity_name.ilike(pattern),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)

        if source_column:
            query = query.where(BusinessEntityMaster.source_column == source_column)
            count_query = count_query.where(BusinessEntityMaster.source_column == source_column)

        if classification_status:
            query = query.where(
                BusinessEntityMaster.classification_status == classification_status
            )
            count_query = count_query.where(
                BusinessEntityMaster.classification_status == classification_status
            )

        sort_field = sort_by if sort_by in SORTABLE_FIELDS else "movement_count"
        sort_column = getattr(BusinessEntityMaster, sort_field)
        order = sort_column.desc() if sort_dir.lower() == "desc" else sort_column.asc()
        query = query.order_by(order, BusinessEntityMaster.entity_id.asc())

        offset = (page - 1) * page_size
        total = self.session.scalar(count_query) or 0
        rows = self.session.scalars(query.offset(offset).limit(page_size)).all()
        return list(rows), int(total)

    def get_by_code(
        self,
        entity_code: str,
        *,
        source_column: str | None = None,
    ) -> list[BusinessEntityMaster]:
        query = select(BusinessEntityMaster).where(BusinessEntityMaster.entity_code == entity_code)
        if source_column:
            query = query.where(BusinessEntityMaster.source_column == source_column)
        return list(self.session.scalars(query.order_by(BusinessEntityMaster.source_column)).all())

    def get_statistics_breakdown(self) -> tuple[dict[str, int], dict[str, int]]:
        by_source = {
            row[0]: int(row[1])
            for row in self.session.execute(
                select(BusinessEntityMaster.source_column, func.count())
                .group_by(BusinessEntityMaster.source_column)
                .order_by(BusinessEntityMaster.source_column)
            ).all()
        }
        by_status = {
            row[0]: int(row[1])
            for row in self.session.execute(
                select(BusinessEntityMaster.classification_status, func.count())
                .group_by(BusinessEntityMaster.classification_status)
                .order_by(BusinessEntityMaster.classification_status)
            ).all()
        }
        return by_source, by_status

    def upsert_entity(
        self,
        *,
        entity_code: str,
        entity_name: str,
        source_system: str,
        source_table: str,
        source_column: str,
        movement_count: int,
        movement_amount: Decimal,
        first_seen: date | None,
        last_seen: date | None,
        classification_status: str,
        confidence: str | None,
        now: datetime,
    ) -> tuple[BusinessEntityMaster, bool]:
        existing = self.session.scalar(
            select(BusinessEntityMaster).where(
                BusinessEntityMaster.source_system == source_system,
                BusinessEntityMaster.source_table == source_table,
                BusinessEntityMaster.source_column == source_column,
                BusinessEntityMaster.entity_code == entity_code,
            )
        )
        if existing is None:
            entity = BusinessEntityMaster(
                entity_code=entity_code,
                entity_name=entity_name,
                source_system=source_system,
                source_table=source_table,
                source_column=source_column,
                movement_count=movement_count,
                movement_amount=movement_amount,
                first_seen=first_seen,
                last_seen=last_seen,
                classification_status=classification_status,
                confidence=confidence,
                created_at=now,
                updated_at=now,
            )
            self.session.add(entity)
            return entity, True

        existing.entity_name = entity_name
        existing.movement_count = movement_count
        existing.movement_amount = movement_amount
        existing.first_seen = first_seen
        existing.last_seen = last_seen
        existing.updated_at = now
        if confidence is not None:
            existing.confidence = confidence
        return existing, False

    def fetch_discovered_entities(self) -> list[dict]:
        """Extrae entidades desde movimientos_diario (solo lectura en origen)."""
        queries = [
            (
                "account_display_value",
                "nombre_cuenta",
                """
                SELECT
                    account_display_value AS entity_code,
                    MAX(nombre_cuenta) AS entity_name,
                    COUNT(*)::BIGINT AS movement_count,
                    COALESCE(SUM(ABS(monto)), 0) AS movement_amount,
                    MIN(fecha) AS first_seen,
                    MAX(fecha) AS last_seen
                FROM movimientos_diario
                GROUP BY account_display_value
                """,
            ),
            (
                "cuenta_proveedor",
                "nombre_proveedor",
                """
                SELECT
                    cuenta_proveedor AS entity_code,
                    MAX(nombre_proveedor) AS entity_name,
                    COUNT(*)::BIGINT AS movement_count,
                    COALESCE(SUM(ABS(monto)), 0) AS movement_amount,
                    MIN(fecha) AS first_seen,
                    MAX(fecha) AS last_seen
                FROM movimientos_diario
                WHERE cuenta_proveedor IS NOT NULL
                  AND nombre_proveedor IS NOT NULL
                GROUP BY cuenta_proveedor
                """,
            ),
            (
                "cuenta_cliente",
                "nombre_cliente",
                """
                SELECT
                    cuenta_cliente AS entity_code,
                    MAX(nombre_cliente) AS entity_name,
                    COUNT(*)::BIGINT AS movement_count,
                    COALESCE(SUM(ABS(monto)), 0) AS movement_amount,
                    MIN(fecha) AS first_seen,
                    MAX(fecha) AS last_seen
                FROM movimientos_diario
                WHERE cuenta_cliente IS NOT NULL
                  AND nombre_cliente IS NOT NULL
                GROUP BY cuenta_cliente
                """,
            ),
        ]

        results: list[dict] = []
        for source_column, _name_column, sql in queries:
            rows = self.session.execute(text(sql)).mappings().all()
            for row in rows:
                results.append(
                    {
                        "entity_code": str(row["entity_code"]),
                        "entity_name": str(row["entity_name"] or "").strip(),
                        "source_column": source_column,
                        "movement_count": int(row["movement_count"]),
                        "movement_amount": Decimal(str(row["movement_amount"])),
                        "first_seen": row["first_seen"],
                        "last_seen": row["last_seen"],
                    }
                )
        return results

    def find_health_issues(self) -> dict[str, list[dict]]:
        duplicated = self.session.execute(
            text(
                """
                SELECT entity_code, COUNT(*) AS occurrences
                FROM business_entity_master
                GROUP BY entity_code
                HAVING COUNT(*) > 1
                ORDER BY occurrences DESC, entity_code ASC
                LIMIT 100
                """
            )
        ).mappings().all()

        empty_names = self.session.execute(
            text(
                """
                SELECT entity_id, entity_code, source_column
                FROM business_entity_master
                WHERE TRIM(entity_name) = ''
                ORDER BY entity_id ASC
                LIMIT 100
                """
            )
        ).mappings().all()

        inconsistent_dates = self.session.execute(
            text(
                """
                SELECT entity_id, entity_code, first_seen, last_seen
                FROM business_entity_master
                WHERE first_seen IS NOT NULL
                  AND last_seen IS NOT NULL
                  AND first_seen > last_seen
                ORDER BY entity_id ASC
                LIMIT 100
                """
            )
        ).mappings().all()

        inconsistent_amounts = self.session.execute(
            text(
                """
                SELECT entity_id, entity_code, movement_count, movement_amount
                FROM business_entity_master
                WHERE movement_count < 0
                   OR movement_amount < 0
                ORDER BY entity_id ASC
                LIMIT 100
                """
            )
        ).mappings().all()

        return {
            "duplicated_codes": [dict(row) for row in duplicated],
            "empty_names": [dict(row) for row in empty_names],
            "inconsistent_dates": [dict(row) for row in inconsistent_dates],
            "inconsistent_amounts": [dict(row) for row in inconsistent_amounts],
        }
