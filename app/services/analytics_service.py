from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status

from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    ClienteResponse,
    CuentaResponse,
    EntidadPrincipalResponse,
    EvolucionClienteResponse,
    EvolucionCuentaResponse,
    EvolucionProveedorResponse,
    KPIEjecutivosResponse,
    KPIResponse,
    MesActividadResponse,
    MesVolumenResponse,
    ProveedorResponse,
    ResumenMensualResponse,
)


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self.repository = repository

    def get_kpis(self) -> KPIResponse:
        return KPIResponse(
            movimientos=self.repository.count_movimientos(),
            clientes=self.repository.count_clientes(),
            proveedores=self.repository.count_proveedores(),
            cuentas=self.repository.count_cuentas(),
            divisas=self.repository.count_divisas(),
        )

    def get_kpis_ejecutivos(self) -> KPIEjecutivosResponse:
        row = self.repository.fetch_kpis_ejecutivos()
        return KPIEjecutivosResponse(
            volumen_total=row["volumen_total"],
            movimiento_promedio=Decimal(row["movimiento_promedio"]).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            mes_mayor_actividad=MesActividadResponse(
                anio=row["actividad_anio"],
                mes=row["actividad_mes"],
                movimientos=row["actividad_movimientos"],
            ),
            mes_mayor_volumen=MesVolumenResponse(
                anio=row["volumen_anio"],
                mes=row["volumen_mes"],
                monto_total=row["volumen_mes_total"],
            ),
            cliente_principal=EntidadPrincipalResponse(
                codigo=row["cliente_codigo"],
                nombre=row["cliente_nombre"],
                movimientos=row["cliente_movimientos"],
                monto_total=row["cliente_monto_total"],
            ),
            proveedor_principal=EntidadPrincipalResponse(
                codigo=row["proveedor_codigo"],
                nombre=row["proveedor_nombre"],
                movimientos=row["proveedor_movimientos"],
                monto_total=row["proveedor_monto_total"],
            ),
            cuenta_principal=EntidadPrincipalResponse(
                codigo=row["cuenta_codigo"],
                nombre=row["cuenta_nombre"],
                movimientos=row["cuenta_movimientos"],
                monto_total=row["cuenta_monto_total"],
            ),
            top_5_clientes_participacion=row["top_5_clientes_participacion"],
            top_10_clientes_participacion=row["top_10_clientes_participacion"],
        )

    def get_top_clientes(self, limit: int) -> list[ClienteResponse]:
        self._validate_limit(limit)
        rows = self.repository.fetch_top_clientes(limit)
        return [ClienteResponse(**row) for row in rows]

    def get_top_proveedores(self, limit: int) -> list[ProveedorResponse]:
        self._validate_limit(limit)
        rows = self.repository.fetch_top_proveedores(limit)
        return [ProveedorResponse(**row) for row in rows]

    def get_top_cuentas(self, limit: int) -> list[CuentaResponse]:
        self._validate_limit(limit)
        rows = self.repository.fetch_top_cuentas(limit)
        return [CuentaResponse(**row) for row in rows]

    def get_evolucion_cliente(self, cliente_codigo: str) -> list[EvolucionClienteResponse]:
        rows = self.repository.fetch_evolucion_cliente(cliente_codigo.strip())
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente no encontrado: {cliente_codigo}",
            )
        return [EvolucionClienteResponse(**row) for row in rows]

    def get_evolucion_proveedor(self, proveedor_codigo: str) -> list[EvolucionProveedorResponse]:
        rows = self.repository.fetch_evolucion_proveedor(proveedor_codigo.strip())
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor no encontrado: {proveedor_codigo}",
            )
        return [EvolucionProveedorResponse(**row) for row in rows]

    def get_evolucion_cuenta(self, cuenta_codigo: str) -> list[EvolucionCuentaResponse]:
        rows = self.repository.fetch_evolucion_cuenta(cuenta_codigo.strip())
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuenta no encontrada: {cuenta_codigo}",
            )
        return [EvolucionCuentaResponse(**row) for row in rows]

    def get_resumen_mensual(self) -> list[ResumenMensualResponse]:
        rows = self.repository.fetch_resumen_mensual()
        return [ResumenMensualResponse(**row) for row in rows]

    @staticmethod
    def _validate_limit(limit: int) -> None:
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="limit debe estar entre 1 y 100",
            )
