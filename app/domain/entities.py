from enum import StrEnum


class BusinessEntity(StrEnum):
    CLIENTE = "CLIENTE"
    PROVEEDOR = "PROVEEDOR"
    CUENTA = "CUENTA"
    TRANSACCION = "TRANSACCION"
    MOVIMIENTO = "MOVIMIENTO"
    MES = "MES"
    ANIO = "ANIO"
