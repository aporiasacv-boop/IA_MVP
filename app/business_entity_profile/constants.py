SORTABLE_PROFILE_FIELDS = frozenset({
    "total_movements",
    "total_amount",
    "average_amount",
    "first_seen",
    "last_seen",
    "active_months",
    "profile_completeness",
    "related_accounts_count",
    "related_counterparties_count",
})

TOP_RELATIONSHIPS_LIMIT = 10

ENTITY_MOVEMENTS_CTE = """
WITH entity_movement_keys AS (
    SELECT DISTINCT ber.canonical_id, md.id AS movement_id
    FROM business_entity_resolution ber
    INNER JOIN business_entity_master bem ON bem.entity_id = ber.entity_id
    INNER JOIN movimientos_diario md ON (
        (bem.source_column = 'account_display_value'
         AND md.account_display_value = bem.entity_code)
     OR (bem.source_column = 'cuenta_proveedor'
         AND md.cuenta_proveedor IS NOT NULL
         AND md.cuenta_proveedor = bem.entity_code)
     OR (bem.source_column = 'cuenta_cliente'
         AND md.cuenta_cliente IS NOT NULL
         AND md.cuenta_cliente = bem.entity_code)
    )
),
entity_movements AS (
    SELECT emk.canonical_id, md.*
    FROM entity_movement_keys emk
    INNER JOIN movimientos_diario md ON md.id = emk.movement_id
),
own_codes AS (
    SELECT ber.canonical_id, bem.entity_code
    FROM business_entity_resolution ber
    INNER JOIN business_entity_master bem ON bem.entity_id = ber.entity_id
)
"""
