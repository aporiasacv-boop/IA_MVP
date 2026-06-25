from enum import StrEnum


class ClarificationSlot(StrEnum):
    CLIENTE_CODIGO = "cliente_codigo"
    PROVEEDOR_CODIGO = "proveedor_codigo"
    CUENTA_CODIGO = "cuenta_codigo"
    MES = "mes"
    ANIO = "anio"
