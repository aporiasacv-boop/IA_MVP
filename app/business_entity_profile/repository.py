from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.business_entity_profile.completeness import compute_debit_credit_ratio, compute_profile_completeness
from app.business_entity_profile.constants import ENTITY_MOVEMENTS_CTE, SORTABLE_PROFILE_FIELDS, TOP_RELATIONSHIPS_LIMIT
from app.models.business_entity_profile import BusinessEntityProfile
from app.models.canonical_business_entity import CanonicalBusinessEntity


class BusinessEntityProfileRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_profiles(self) -> int:
        return self.session.scalar(select(func.count()).select_from(BusinessEntityProfile)) or 0

    def count_canonical(self) -> int:
        return self.session.scalar(select(func.count()).select_from(CanonicalBusinessEntity)) or 0

    def count_profiles_without_movements(self) -> int:
        return (
            self.session.scalar(
                select(func.count())
                .select_from(BusinessEntityProfile)
                .where(BusinessEntityProfile.total_movements == 0)
            )
            or 0
        )

    def average_profile_completeness(self) -> float:
        value = self.session.scalar(select(func.avg(BusinessEntityProfile.profile_completeness)))
        return round(float(value or 0), 4)

    def sum_total_movements(self) -> int:
        return int(
            self.session.scalar(select(func.coalesce(func.sum(BusinessEntityProfile.total_movements), 0))) or 0
        )

    def get_last_refresh(self) -> datetime | None:
        return self.session.scalar(select(func.max(BusinessEntityProfile.generated_at)))

    def list_canonical_ids(self) -> list[int]:
        rows = self.session.scalars(
            select(CanonicalBusinessEntity.canonical_id).order_by(CanonicalBusinessEntity.canonical_id)
        ).all()
        return [int(row) for row in rows]

    def fetch_scalar_aggregates(self) -> list[dict]:
        sql = (
            ENTITY_MOVEMENTS_CTE
            + """
SELECT
    cbe.canonical_id,
    COALESCE(agg.total_movements, 0) AS total_movements,
    COALESCE(agg.total_amount, 0) AS total_amount,
    COALESCE(agg.average_amount, 0) AS average_amount,
    agg.first_seen,
    agg.last_seen,
    COALESCE(agg.active_months, 0) AS active_months,
    COALESCE(agg.active_days, 0) AS active_days,
    COALESCE(agg.debit_amount, 0) AS debit_amount,
    COALESCE(agg.credit_amount, 0) AS credit_amount,
    COALESCE(agg.related_accounts_count, 0) AS related_accounts_count,
    COALESCE(cp.related_counterparties_count, 0) AS related_counterparties_count,
    COALESCE(dim.dimensions_used, '[]'::jsonb) AS dimensions_used
FROM canonical_business_entity cbe
LEFT JOIN (
    SELECT
        canonical_id,
        COUNT(*) AS total_movements,
        SUM(monto) AS total_amount,
        AVG(monto) AS average_amount,
        MIN(fecha) AS first_seen,
        MAX(fecha) AS last_seen,
        COUNT(DISTINCT (anio::text || '-' || lpad(mes::text, 2, '0'))) AS active_months,
        COUNT(DISTINCT fecha) AS active_days,
        SUM(CASE WHEN monto > 0 THEN monto ELSE 0 END) AS debit_amount,
        SUM(CASE WHEN monto < 0 THEN ABS(monto) ELSE 0 END) AS credit_amount,
        COUNT(DISTINCT account_display_value) AS related_accounts_count
    FROM entity_movements
    GROUP BY canonical_id
) agg ON agg.canonical_id = cbe.canonical_id
LEFT JOIN (
    SELECT canonical_id, COUNT(DISTINCT cp_code) AS related_counterparties_count
    FROM (
        SELECT em.canonical_id, em.cuenta_proveedor AS cp_code
        FROM entity_movements em
        WHERE em.cuenta_proveedor IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM own_codes oc
              WHERE oc.canonical_id = em.canonical_id
                AND oc.entity_code = em.cuenta_proveedor
          )
        UNION
        SELECT em.canonical_id, em.cuenta_cliente AS cp_code
        FROM entity_movements em
        WHERE em.cuenta_cliente IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM own_codes oc
              WHERE oc.canonical_id = em.canonical_id
                AND oc.entity_code = em.cuenta_cliente
          )
    ) counterparty_codes
    GROUP BY canonical_id
) cp ON cp.canonical_id = cbe.canonical_id
LEFT JOIN (
    SELECT ber.canonical_id,
           jsonb_agg(DISTINCT bem.source_column ORDER BY bem.source_column) AS dimensions_used
    FROM business_entity_resolution ber
    INNER JOIN business_entity_master bem ON bem.entity_id = ber.entity_id
    GROUP BY ber.canonical_id
) dim ON dim.canonical_id = cbe.canonical_id
ORDER BY cbe.canonical_id
"""
        )
        return [dict(row) for row in self.session.execute(text(sql)).mappings().all()]

    def fetch_monthly_distributions(self) -> dict[int, dict]:
        sql = (
            ENTITY_MOVEMENTS_CTE
            + """
SELECT canonical_id,
       jsonb_object_agg(
           period_key,
           jsonb_build_object(
               'movements', movements,
               'amount', amount,
               'debit', debit,
               'credit', credit
           )
       ) AS monthly_distribution
FROM (
    SELECT
        canonical_id,
        anio::text || '-' || lpad(mes::text, 2, '0') AS period_key,
        COUNT(*) AS movements,
        SUM(monto) AS amount,
        SUM(CASE WHEN monto > 0 THEN monto ELSE 0 END) AS debit,
        SUM(CASE WHEN monto < 0 THEN ABS(monto) ELSE 0 END) AS credit
    FROM entity_movements
    GROUP BY canonical_id, anio, mes
) monthly
GROUP BY canonical_id
"""
        )
        result: dict[int, dict] = {}
        for row in self.session.execute(text(sql)).mappings().all():
            result[int(row["canonical_id"])] = dict(row["monthly_distribution"] or {})
        return result

    def fetch_currencies(self) -> dict[int, list[str]]:
        sql = (
            ENTITY_MOVEMENTS_CTE
            + """
SELECT canonical_id, jsonb_agg(DISTINCT divisa ORDER BY divisa) AS currencies
FROM entity_movements
GROUP BY canonical_id
"""
        )
        result: dict[int, list[str]] = {}
        for row in self.session.execute(text(sql)).mappings().all():
            result[int(row["canonical_id"])] = list(row["currencies"] or [])
        return result

    def fetch_journals(self) -> dict[int, dict]:
        sql = (
            ENTITY_MOVEMENTS_CTE
            + """
, journal_stats AS (
    SELECT canonical_id, numero_diario, COUNT(*) AS movements
    FROM entity_movements
    GROUP BY canonical_id, numero_diario
),
journal_totals AS (
    SELECT canonical_id, COUNT(*) AS distinct_count
    FROM journal_stats
    GROUP BY canonical_id
),
journal_top AS (
    SELECT canonical_id,
           jsonb_agg(
               jsonb_build_object('numero', numero_diario, 'movements', movements)
               ORDER BY movements DESC
           ) AS top
    FROM (
        SELECT canonical_id, numero_diario, movements,
               ROW_NUMBER() OVER (PARTITION BY canonical_id ORDER BY movements DESC) AS rn
        FROM journal_stats
    ) ranked
    WHERE rn <= :limit
    GROUP BY canonical_id
)
SELECT jtot.canonical_id, jtot.distinct_count, COALESCE(jtop.top, '[]'::jsonb) AS top
FROM journal_totals jtot
LEFT JOIN journal_top jtop ON jtop.canonical_id = jtot.canonical_id
"""
        )
        result: dict[int, dict] = {}
        for row in self.session.execute(text(sql), {"limit": TOP_RELATIONSHIPS_LIMIT}).mappings().all():
            top = row["top"] or []
            if isinstance(top, list) and len(top) > TOP_RELATIONSHIPS_LIMIT:
                top = top[:TOP_RELATIONSHIPS_LIMIT]
            result[int(row["canonical_id"])] = {
                "distinct_count": int(row["distinct_count"] or 0),
                "top": top,
            }
        return result

    def fetch_top_accounts(self) -> dict[int, list[dict]]:
        sql = (
            ENTITY_MOVEMENTS_CTE
            + """
, account_stats AS (
    SELECT canonical_id, account_display_value, nombre_cuenta,
           COUNT(*) AS movements, SUM(monto) AS amount
    FROM entity_movements
    GROUP BY canonical_id, account_display_value, nombre_cuenta
)
SELECT canonical_id,
       jsonb_agg(
           jsonb_build_object(
               'code', account_display_value,
               'name', nombre_cuenta,
               'movements', movements,
               'amount', amount
           )
           ORDER BY movements DESC
       ) AS top_accounts
FROM (
    SELECT canonical_id, account_display_value, nombre_cuenta, movements, amount,
           ROW_NUMBER() OVER (
               PARTITION BY canonical_id ORDER BY movements DESC, ABS(amount) DESC
           ) AS rn
    FROM account_stats
) ranked
WHERE rn <= :limit
GROUP BY canonical_id
"""
        )
        result: dict[int, list[dict]] = {}
        for row in self.session.execute(text(sql), {"limit": TOP_RELATIONSHIPS_LIMIT}).mappings().all():
            items = row["top_accounts"] or []
            result[int(row["canonical_id"])] = items[:TOP_RELATIONSHIPS_LIMIT]
        return result

    def fetch_top_counterparties(self) -> dict[int, list[dict]]:
        sql = (
            ENTITY_MOVEMENTS_CTE
            + """
, cp_stats AS (
    SELECT em.canonical_id, em.cuenta_proveedor AS cp_code,
           COALESCE(em.nombre_proveedor, '') AS cp_name,
           'cuenta_proveedor' AS cp_dimension,
           COUNT(*) AS movements, SUM(em.monto) AS amount
    FROM entity_movements em
    WHERE em.cuenta_proveedor IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM own_codes oc
          WHERE oc.canonical_id = em.canonical_id AND oc.entity_code = em.cuenta_proveedor
      )
    GROUP BY em.canonical_id, em.cuenta_proveedor, em.nombre_proveedor
    UNION ALL
    SELECT em.canonical_id, em.cuenta_cliente AS cp_code,
           COALESCE(em.nombre_cliente, '') AS cp_name,
           'cuenta_cliente' AS cp_dimension,
           COUNT(*) AS movements, SUM(em.monto) AS amount
    FROM entity_movements em
    WHERE em.cuenta_cliente IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM own_codes oc
          WHERE oc.canonical_id = em.canonical_id AND oc.entity_code = em.cuenta_cliente
      )
    GROUP BY em.canonical_id, em.cuenta_cliente, em.nombre_cliente
)
SELECT canonical_id,
       jsonb_agg(
           jsonb_build_object(
               'code', cp_code,
               'name', cp_name,
               'dimension', cp_dimension,
               'movements', movements,
               'amount', amount
           )
           ORDER BY movements DESC
       ) AS top_counterparties
FROM (
    SELECT canonical_id, cp_code, cp_name, cp_dimension, movements, amount,
           ROW_NUMBER() OVER (PARTITION BY canonical_id ORDER BY movements DESC) AS rn
    FROM cp_stats
) ranked
WHERE rn <= :limit
GROUP BY canonical_id
"""
        )
        result: dict[int, list[dict]] = {}
        for row in self.session.execute(text(sql), {"limit": TOP_RELATIONSHIPS_LIMIT}).mappings().all():
            items = row["top_counterparties"] or []
            result[int(row["canonical_id"])] = items[:TOP_RELATIONSHIPS_LIMIT]
        return result

    def get_profile_by_canonical_id(self, canonical_id: int) -> BusinessEntityProfile | None:
        return self.session.scalar(
            select(BusinessEntityProfile).where(BusinessEntityProfile.canonical_id == canonical_id)
        )

    def upsert_profile(
        self,
        *,
        canonical_id: int,
        total_movements: int,
        total_amount: Decimal,
        average_amount: Decimal,
        first_seen: date | None,
        last_seen: date | None,
        active_months: int,
        active_days: int,
        debit_amount: Decimal,
        credit_amount: Decimal,
        debit_credit_ratio: Decimal | None,
        related_accounts_count: int,
        related_counterparties_count: int,
        monthly_distribution: dict,
        currencies: list,
        journals: dict,
        dimensions_used: list,
        top_accounts: list,
        top_counterparties: list,
        profile_completeness: Decimal,
        generated_at: datetime,
    ) -> tuple[BusinessEntityProfile, bool]:
        existing = self.get_profile_by_canonical_id(canonical_id)
        is_new = existing is None
        profile = existing or BusinessEntityProfile(
            canonical_id=canonical_id,
            created_at=generated_at,
        )
        profile.total_movements = total_movements
        profile.total_amount = total_amount
        profile.average_amount = average_amount
        profile.first_seen = first_seen
        profile.last_seen = last_seen
        profile.active_months = active_months
        profile.active_days = active_days
        profile.debit_amount = debit_amount
        profile.credit_amount = credit_amount
        profile.debit_credit_ratio = debit_credit_ratio
        profile.related_accounts_count = related_accounts_count
        profile.related_counterparties_count = related_counterparties_count
        profile.monthly_distribution = monthly_distribution
        profile.currencies = currencies
        profile.journals = journals
        profile.dimensions_used = dimensions_used
        profile.top_accounts = top_accounts
        profile.top_counterparties = top_counterparties
        profile.profile_completeness = profile_completeness
        profile.generated_at = generated_at
        profile.updated_at = generated_at
        if is_new:
            self.session.add(profile)
        return profile, is_new

    def list_profiles(
        self,
        *,
        search: str | None = None,
        sort_by: str = "total_movements",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict], int]:
        conditions = ["1=1"]
        params: dict = {"limit": page_size, "offset": (page - 1) * page_size}
        if search:
            conditions.append(
                "(cbe.canonical_name ILIKE :search OR cbe.normalized_name ILIKE :search "
                "OR cbe.primary_rfc ILIKE :search)"
            )
            params["search"] = f"%{search.strip()}%"

        sort_field = sort_by if sort_by in SORTABLE_PROFILE_FIELDS else "total_movements"
        order = "DESC" if sort_dir.lower() == "desc" else "ASC"
        where_clause = " AND ".join(conditions)

        total = self.session.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM business_entity_profile bep
                INNER JOIN canonical_business_entity cbe ON cbe.canonical_id = bep.canonical_id
                WHERE {where_clause}
                """
            ),
            params,
        ).scalar_one()

        rows = self.session.execute(
            text(
                f"""
                SELECT
                    bep.*,
                    cbe.canonical_name,
                    cbe.primary_rfc
                FROM business_entity_profile bep
                INNER JOIN canonical_business_entity cbe ON cbe.canonical_id = bep.canonical_id
                WHERE {where_clause}
                ORDER BY bep.{sort_field} {order}, bep.canonical_id ASC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()
        return [dict(row) for row in rows], int(total)

    def get_profile_detail(self, canonical_id: int) -> dict | None:
        row = self.session.execute(
            text(
                """
                SELECT bep.*, cbe.canonical_name, cbe.primary_rfc
                FROM business_entity_profile bep
                INNER JOIN canonical_business_entity cbe ON cbe.canonical_id = bep.canonical_id
                WHERE bep.canonical_id = :canonical_id
                """
            ),
            {"canonical_id": canonical_id},
        ).mappings().first()
        return dict(row) if row else None

    def find_health_issues(self) -> dict[str, list[dict]]:
        inconsistent = self.session.execute(
            text(
                """
                SELECT profile_id, canonical_id, total_amount, debit_amount, credit_amount
                FROM business_entity_profile
                WHERE total_movements > 0
                  AND ABS((debit_amount - credit_amount) - total_amount) > 0.01
                LIMIT 100
                """
            )
        ).mappings().all()

        invalid_dates = self.session.execute(
            text(
                """
                SELECT profile_id, canonical_id, first_seen, last_seen
                FROM business_entity_profile
                WHERE first_seen IS NOT NULL AND last_seen IS NOT NULL AND first_seen > last_seen
                LIMIT 100
                """
            )
        ).mappings().all()

        incomplete = self.session.execute(
            text(
                """
                SELECT profile_id, canonical_id, active_months,
                       jsonb_object_length(monthly_distribution) AS distribution_months
                FROM business_entity_profile
                WHERE total_movements > 0
                  AND active_months > 0
                  AND jsonb_object_length(monthly_distribution) != active_months
                LIMIT 100
                """
            )
        ).mappings().all()

        without_movements = self.session.execute(
            text(
                """
                SELECT profile_id, canonical_id
                FROM business_entity_profile
                WHERE total_movements = 0
                LIMIT 100
                """
            )
        ).mappings().all()

        no_relations = self.session.execute(
            text(
                """
                SELECT profile_id, canonical_id
                FROM business_entity_profile
                WHERE total_movements > 0
                  AND related_accounts_count = 0
                  AND related_counterparties_count = 0
                LIMIT 100
                """
            )
        ).mappings().all()

        return {
            "inconsistent_amounts": [dict(row) for row in inconsistent],
            "invalid_dates": [dict(row) for row in invalid_dates],
            "incomplete_distributions": [dict(row) for row in incomplete],
            "profiles_without_movements": [dict(row) for row in without_movements],
            "entities_without_relations": [dict(row) for row in no_relations],
        }
