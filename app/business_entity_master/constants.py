SOURCE_SYSTEM_D365 = "D365_FO"
SOURCE_TABLE_MOVIMIENTOS = "movimientos_diario"

SOURCE_COLUMN_ACCOUNT = "account_display_value"
SOURCE_COLUMN_VENDOR = "cuenta_proveedor"
SOURCE_COLUMN_CUSTOMER = "cuenta_cliente"

CLASSIFICATION_PENDING = "pending"

SORTABLE_FIELDS = frozenset({
    "entity_code",
    "entity_name",
    "movement_count",
    "movement_amount",
    "first_seen",
    "last_seen",
    "updated_at",
})
