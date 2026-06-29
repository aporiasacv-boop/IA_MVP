from app.query_engine.query_types import BusinessQueryType
from app.query_executor.query_result import BusinessQueryResult
from app.response_engine.response_result import BusinessResponse
from app.response_engine.response_templates import (
    CAPABILITY_LABELS,
    CAPABILITY_DISPLAY_ORDER,
    COUNT_CLIENTES_TEMPLATE,
    COUNT_PROVEEDORES_TEMPLATE,
    DATASET_INFO_HEADER,
    DATA_COVERAGE_TEMPLATE,
    KPIS_TEMPLATE,
    MAX_PROVEEDOR_MES_TEMPLATE,
    SYSTEM_CAPABILITIES_HEADER,
    TOP_CLIENTES_HEADER,
    TOP_PROVEEDORES_HEADER,
    UNSUPPORTED_TEMPLATE,
)


class DeterministicResponseEngine:
    def generate(self, query_result: BusinessQueryResult) -> BusinessResponse:
        if not query_result.success:
            return self._unsupported_response(query_result)

        query_type = query_result.query_type
        data = query_result.data

        if query_type == BusinessQueryType.COUNT_CLIENTES:
            return self._success(
                query_type,
                COUNT_CLIENTES_TEMPLATE.format(total=data.get("total", 0)),
                query_result,
            )

        if query_type == BusinessQueryType.COUNT_PROVEEDORES:
            return self._success(
                query_type,
                COUNT_PROVEEDORES_TEMPLATE.format(total=data.get("total", 0)),
                query_result,
            )

        if query_type == BusinessQueryType.TOP_CLIENTES:
            return self._success(
                query_type,
                self._format_top_clientes(data.get("items", [])),
                query_result,
            )

        if query_type == BusinessQueryType.TOP_PROVEEDORES:
            return self._success(
                query_type,
                self._format_top_proveedores(data.get("items", [])),
                query_result,
            )

        if query_type == BusinessQueryType.MAX_PROVEEDOR_MES:
            return self._success(
                query_type,
                self._format_max_proveedor_mes(data),
                query_result,
            )

        if query_type == BusinessQueryType.SYSTEM_CAPABILITIES:
            return self._success(
                query_type,
                self._format_system_capabilities(data),
                query_result,
            )

        if query_type == BusinessQueryType.DATA_COVERAGE:
            return self._success(
                query_type,
                DATA_COVERAGE_TEMPLATE.format(
                    fecha_min=data.get("fecha_min", "—"),
                    fecha_max=data.get("fecha_max", "—"),
                ),
                query_result,
            )

        if query_type == BusinessQueryType.DATASET_INFO:
            return self._success(
                query_type,
                self._format_dataset_info(data),
                query_result,
            )

        if query_type == BusinessQueryType.KPIS:
            return self._success(
                query_type,
                KPIS_TEMPLATE.format(
                    movimientos=int(data.get("movimientos", 0)),
                    clientes=int(data.get("clientes", 0)),
                    proveedores=int(data.get("proveedores", 0)),
                    cuentas=int(data.get("cuentas", 0)),
                    divisas=int(data.get("divisas", 0)),
                ),
                query_result,
            )

        return self._unsupported_response(query_result)

    @staticmethod
    def _format_top_clientes(items: list[dict]) -> str:
        lines = [TOP_CLIENTES_HEADER, ""]
        if not items:
            lines.append("No se encontraron clientes para mostrar.")
            return "\n".join(lines)

        for index, item in enumerate(items, start=1):
            nombre = item.get("cliente_nombre", "Sin nombre")
            codigo = item.get("cliente_codigo", "")
            movimientos = item.get("movimientos", 0)
            lines.append(f"{index}. {nombre} ({codigo}) — {movimientos} movimientos")
        return "\n".join(lines)

    @staticmethod
    def _format_top_proveedores(items: list[dict]) -> str:
        lines = [TOP_PROVEEDORES_HEADER, ""]
        if not items:
            lines.append("No se encontraron proveedores para mostrar.")
            return "\n".join(lines)

        for index, item in enumerate(items, start=1):
            nombre = item.get("proveedor_nombre", "Sin nombre")
            codigo = item.get("proveedor_codigo", "")
            movimientos = item.get("movimientos", 0)
            lines.append(f"{index}. {nombre} ({codigo}) — {movimientos} movimientos")
        return "\n".join(lines)

    @staticmethod
    def _format_max_proveedor_mes(data: dict) -> str:
        proveedor = data.get("proveedor_nombre") or data.get("proveedor") or data.get(
            "proveedor_codigo",
            "desconocido",
        )
        monto_total = data.get("monto_total", 0)
        return MAX_PROVEEDOR_MES_TEMPLATE.format(
            proveedor=proveedor,
            monto_total=DeterministicResponseEngine._format_amount(monto_total),
        )

    @staticmethod
    def _format_amount(value: object) -> str:
        if isinstance(value, (int, float)):
            return f"{value:,.2f}"
        return str(value)

    @staticmethod
    def _format_system_capabilities(data: dict) -> str:
        display_data = dict(data)
        if display_data.get("top_clientes") and display_data.get("top_proveedores"):
            display_data["rankings"] = True

        lines = [SYSTEM_CAPABILITIES_HEADER, ""]
        for key in CAPABILITY_DISPLAY_ORDER:
            if display_data.get(key):
                lines.append(f"• {CAPABILITY_LABELS[key]}")
        return "\n".join(lines)

    @staticmethod
    def _format_dataset_info(data: dict) -> str:
        movimientos = int(data.get("total_movimientos", 0))
        clientes = int(data.get("total_clientes", 0))
        proveedores = int(data.get("total_proveedores", 0))
        return (
            f"{DATASET_INFO_HEADER}\n\n"
            f"• {movimientos:,} movimientos\n"
            f"• {clientes:,} clientes\n"
            f"• {proveedores:,} proveedores"
        )

    @staticmethod
    def _success(
        query_type: str,
        answer: str,
        query_result: BusinessQueryResult,
    ) -> BusinessResponse:
        return BusinessResponse(
            success=True,
            answer=answer,
            query_type=query_type,
            metadata={"query_metadata": query_result.metadata},
        )

    @staticmethod
    def _unsupported_response(query_result: BusinessQueryResult) -> BusinessResponse:
        return BusinessResponse(
            success=False,
            answer=UNSUPPORTED_TEMPLATE,
            query_type=query_result.query_type,
            metadata={"query_metadata": query_result.metadata},
        )
