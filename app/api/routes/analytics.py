from fastapi import APIRouter, Depends, Query

from app.api.deps import get_analytics_service
from app.schemas.analytics import (
    ClienteResponse,
    CuentaResponse,
    EvolucionClienteResponse,
    EvolucionCuentaResponse,
    EvolucionProveedorResponse,
    KPIEjecutivosResponse,
    KPIResponse,
    ProveedorResponse,
    ResumenMensualResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get(
    "/kpis",
    response_model=KPIResponse,
    summary="Indicadores clave del datamart",
    description="Devuelve totales globales de movimientos, clientes, proveedores, cuentas y divisas.",
)
def get_kpis(service: AnalyticsService = Depends(get_analytics_service)) -> KPIResponse:
    return service.get_kpis()


@router.get(
    "/kpis/ejecutivos",
    response_model=KPIEjecutivosResponse,
    summary="Indicadores ejecutivos del datamart",
    description=(
        "Metricas consolidadas para dashboard y resumenes de direccion. "
        "Consulta exclusivamente tablas fact y materialized views."
    ),
)
def get_kpis_ejecutivos(
    service: AnalyticsService = Depends(get_analytics_service),
) -> KPIEjecutivosResponse:
    return service.get_kpis_ejecutivos()


@router.get(
    "/top-clientes",
    response_model=list[ClienteResponse],
    summary="Ranking de clientes",
    description="Consulta mv_top_clientes ordenado por movimientos.",
)
def get_top_clientes(
    limit: int = Query(default=10, ge=1, le=100, description="Cantidad maxima de registros"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[ClienteResponse]:
    return service.get_top_clientes(limit)


@router.get(
    "/top-proveedores",
    response_model=list[ProveedorResponse],
    summary="Ranking de proveedores",
    description="Consulta mv_top_proveedores ordenado por movimientos.",
)
def get_top_proveedores(
    limit: int = Query(default=10, ge=1, le=100, description="Cantidad maxima de registros"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[ProveedorResponse]:
    return service.get_top_proveedores(limit)


@router.get(
    "/top-cuentas",
    response_model=list[CuentaResponse],
    summary="Ranking de cuentas contables",
    description="Consulta mv_top_cuentas ordenado por movimientos.",
)
def get_top_cuentas(
    limit: int = Query(default=10, ge=1, le=100, description="Cantidad maxima de registros"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[CuentaResponse]:
    return service.get_top_cuentas(limit)


@router.get(
    "/evolucion-cliente/{cliente_codigo}",
    response_model=list[EvolucionClienteResponse],
    summary="Evolucion mensual de un cliente",
    description="Devuelve la serie mensual disponible para el cliente indicado.",
)
def get_evolucion_cliente(
    cliente_codigo: str,
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[EvolucionClienteResponse]:
    return service.get_evolucion_cliente(cliente_codigo)


@router.get(
    "/evolucion-proveedor/{proveedor_codigo}",
    response_model=list[EvolucionProveedorResponse],
    summary="Evolucion mensual de un proveedor",
    description="Devuelve la serie mensual disponible para el proveedor indicado.",
)
def get_evolucion_proveedor(
    proveedor_codigo: str,
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[EvolucionProveedorResponse]:
    return service.get_evolucion_proveedor(proveedor_codigo)


@router.get(
    "/evolucion-cuenta/{cuenta_codigo}",
    response_model=list[EvolucionCuentaResponse],
    summary="Evolucion mensual de una cuenta contable",
    description="Devuelve la serie mensual disponible para la cuenta indicada.",
)
def get_evolucion_cuenta(
    cuenta_codigo: str,
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[EvolucionCuentaResponse]:
    return service.get_evolucion_cuenta(cuenta_codigo)


@router.get(
    "/resumen-mensual",
    response_model=list[ResumenMensualResponse],
    summary="Resumen mensual del ejercicio",
    description="Consulta mv_resumen_mensual con movimientos y montos por mes.",
)
def get_resumen_mensual(
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[ResumenMensualResponse]:
    return service.get_resumen_mensual()
