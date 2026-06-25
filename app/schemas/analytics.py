from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class KPIResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "movimientos": 386480,
            "clientes": 50,
            "proveedores": 766,
            "cuentas": 1962,
            "divisas": 3,
        }
    })

    movimientos: int = Field(description="Total de apuntes contables cargados")
    clientes: int = Field(description="Clientes distintos con actividad")
    proveedores: int = Field(description="Proveedores distintos con actividad")
    cuentas: int = Field(description="Cuentas contables con actividad")
    divisas: int = Field(description="Divisas operativas registradas")


class MesActividadResponse(BaseModel):
    anio: int
    mes: int
    movimientos: int


class MesVolumenResponse(BaseModel):
    anio: int
    mes: int
    monto_total: Decimal


class EntidadPrincipalResponse(BaseModel):
    codigo: str
    nombre: str
    movimientos: int
    monto_total: Decimal


class KPIEjecutivosResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "volumen_total": "32500000000.0000",
            "movimiento_promedio": "32206.67",
            "mes_mayor_actividad": {"anio": 2025, "mes": 6, "movimientos": 37482},
            "mes_mayor_volumen": {"anio": 2025, "mes": 12, "monto_total": "9816295293.9200"},
            "cliente_principal": {
                "codigo": "C0003",
                "nombre": "PUBLICO EN GENERAL",
                "movimientos": 57730,
                "monto_total": "47648780.5000",
            },
            "proveedor_principal": {
                "codigo": "20401001",
                "nombre": "20401001 NOMINA POR PAGAR",
                "movimientos": 15639,
                "monto_total": "370447552.5800",
            },
            "cuenta_principal": {
                "codigo": "20603001",
                "nombre": "IVA TRASLADABLE POR COBRAR",
                "movimientos": 39448,
                "monto_total": "143707764.2400",
            },
            "top_5_clientes_participacion": "45.2500",
            "top_10_clientes_participacion": "78.1200",
        }
    })

    volumen_total: Decimal = Field(description="Suma de volumen mensual del ejercicio")
    movimiento_promedio: Decimal = Field(description="Promedio mensual de movimientos")
    mes_mayor_actividad: MesActividadResponse
    mes_mayor_volumen: MesVolumenResponse
    cliente_principal: EntidadPrincipalResponse
    proveedor_principal: EntidadPrincipalResponse
    cuenta_principal: EntidadPrincipalResponse
    top_5_clientes_participacion: Decimal = Field(description="Porcentaje de volumen top 5 clientes")
    top_10_clientes_participacion: Decimal = Field(description="Porcentaje de volumen top 10 clientes")


class ClienteResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "ranking": 1,
            "cliente_codigo": "C0027",
            "cliente_nombre": "NUEVA WAL MART DE MEXICO",
            "movimientos": 19004,
            "monto_total": "361439922.8800",
            "monto_promedio": "19019.5150",
        }
    })

    ranking: int
    cliente_codigo: str
    cliente_nombre: str
    movimientos: int
    monto_total: Decimal
    monto_promedio: Decimal


class ProveedorResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "ranking": 1,
            "proveedor_codigo": "20401001",
            "proveedor_nombre": "20401001 NOMINA POR PAGAR",
            "movimientos": 15639,
            "monto_total": "370447552.5800",
            "monto_promedio": "23687.2900",
        }
    })

    ranking: int
    proveedor_codigo: str
    proveedor_nombre: str
    movimientos: int
    monto_total: Decimal
    monto_promedio: Decimal


class CuentaResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "ranking": 1,
            "cuenta_codigo": "20603001",
            "cuenta_nombre": "IVA TRASLADABLE POR COBRAR",
            "movimientos": 39448,
            "monto_total": "143707764.2400",
            "monto_promedio": "3642.8900",
        }
    })

    ranking: int
    cuenta_codigo: str
    cuenta_nombre: str
    movimientos: int
    monto_total: Decimal
    monto_promedio: Decimal


class ResumenMensualResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "anio": 2025,
            "mes": 6,
            "movimientos": 37482,
            "monto_total": "1519405346.2600",
            "monto_promedio": "40537.5200",
        }
    })

    anio: int
    mes: int
    movimientos: int
    monto_total: Decimal
    monto_promedio: Decimal


class EvolucionClienteResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "anio": 2025,
            "mes": 3,
            "cliente_codigo": "C0027",
            "cliente_nombre": "NUEVA WAL MART DE MEXICO",
            "movimientos": 2567,
            "monto_total": "60209847.6600",
            "monto_promedio": "23455.3300",
        }
    })

    anio: int
    mes: int
    cliente_codigo: str
    cliente_nombre: str
    movimientos: int
    monto_total: Decimal
    monto_promedio: Decimal


class EvolucionProveedorResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "anio": 2025,
            "mes": 12,
            "proveedor_codigo": "20401001",
            "proveedor_nombre": "20401001 NOMINA POR PAGAR",
            "movimientos": 2326,
            "monto_total": "72672065.3400",
            "monto_promedio": "31243.3700",
        }
    })

    anio: int
    mes: int
    proveedor_codigo: str
    proveedor_nombre: str
    movimientos: int
    monto_total: Decimal
    monto_promedio: Decimal


class EvolucionCuentaResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "anio": 2025,
            "mes": 6,
            "cuenta_codigo": "20603001",
            "cuenta_nombre": "IVA TRASLADABLE POR COBRAR",
            "movimientos": 6369,
            "monto_total": "11727243.8100",
            "monto_promedio": "1841.3000",
        }
    })

    anio: int
    mes: int
    cuenta_codigo: str
    cuenta_nombre: str
    movimientos: int
    monto_total: Decimal
    monto_promedio: Decimal
