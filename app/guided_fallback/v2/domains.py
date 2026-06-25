from enum import StrEnum


class BusinessDomain(StrEnum):
    VENTAS = "VENTAS"
    COMPRAS = "COMPRAS"
    INVENTARIO = "INVENTARIO"
    FACTURACION = "FACTURACION"
    FINANZAS = "FINANZAS"
    LOGISTICA = "LOGISTICA"
    PRODUCCION = "PRODUCCION"


DOMAIN_DISPLAY_LABELS: dict[BusinessDomain, str] = {
    BusinessDomain.VENTAS: "ventas",
    BusinessDomain.COMPRAS: "compras",
    BusinessDomain.INVENTARIO: "inventario",
    BusinessDomain.FACTURACION: "facturación",
    BusinessDomain.FINANZAS: "finanzas",
    BusinessDomain.LOGISTICA: "logística",
    BusinessDomain.PRODUCCION: "producción",
}

DOMAIN_HINTS: dict[BusinessDomain, tuple[str, ...]] = {
    BusinessDomain.VENTAS: ("ventas", "venta", "vender"),
    BusinessDomain.COMPRAS: ("compras", "compra", "compradores"),
    BusinessDomain.INVENTARIO: ("inventario", "existencias", "stock"),
    BusinessDomain.FACTURACION: ("facturacion", "factura", "facturas"),
    BusinessDomain.FINANZAS: ("finanzas", "financiero", "financiera"),
    BusinessDomain.LOGISTICA: ("logistica", "envios", "distribucion"),
    BusinessDomain.PRODUCCION: ("produccion", "manufactura", "fabricacion"),
}

SUPPORTED_CAPABILITIES: tuple[str, ...] = (
    "Clientes",
    "Proveedores",
    "KPIs",
    "Actividad mensual",
)

MAX_VISIBLE_CAPABILITIES = 4
