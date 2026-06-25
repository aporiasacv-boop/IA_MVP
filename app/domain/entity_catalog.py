from app.domain.entities import BusinessEntity

ENTITY_SYNONYMS: dict[BusinessEntity, tuple[str, ...]] = {
    BusinessEntity.CLIENTE: (
        "cliente",
        "clientes",
        "customer",
        "comprador",
        "compradores",
    ),
    BusinessEntity.PROVEEDOR: (
        "proveedor",
        "proveedores",
        "vendor",
        "vendors",
    ),
    BusinessEntity.CUENTA: (
        "cuenta",
        "cuentas",
    ),
    BusinessEntity.TRANSACCION: (
        "transaccion",
        "transacción",
        "movimiento individual",
    ),
    BusinessEntity.MOVIMIENTO: (
        "movimiento",
        "movimientos",
        "actividad",
    ),
    BusinessEntity.MES: (
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ),
    BusinessEntity.ANIO: (
        "año",
        "anio",
        "ejercicio",
    ),
}

MONTH_NAMES: tuple[str, ...] = ENTITY_SYNONYMS[BusinessEntity.MES]
