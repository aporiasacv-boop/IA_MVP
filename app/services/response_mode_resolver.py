from app.schemas.response_mode import ResponseMode
from app.services.intent_router import Intent


class ResponseModeResolver:
    DETERMINISTIC_INTENTS = frozenset({
        Intent.TOP_CLIENTES,
        Intent.BOTTOM_CLIENTES,
        Intent.TOP_PROVEEDORES,
        Intent.BOTTOM_PROVEEDORES,
        Intent.TOP_CUENTAS,
        Intent.BOTTOM_CUENTAS,
        Intent.BEST_MONTH,
        Intent.WORST_MONTH,
        Intent.MONTH_ANALYSIS,
        Intent.DATA_COVERAGE,
        Intent.KPIS,
        Intent.KPIS_EJECUTIVOS,
        Intent.INSIGHTS,
        Intent.CLIENTE_CRECIMIENTO,
        Intent.CLIENTE_CAIDA,
        Intent.PROVEEDOR_CRECIMIENTO,
        Intent.PROVEEDOR_CAIDA,
        Intent.RESUMEN_MENSUAL,
    })

    GENERATIVE_INTENTS = frozenset({
        Intent.EXECUTIVE_SUMMARY,
        Intent.RISKS,
        Intent.OPPORTUNITIES,
        Intent.YEAR_SUMMARY,
        Intent.EXECUTIVE_INSIGHTS,
        Intent.BUSINESS_CONCENTRATION,
        Intent.EVOLUCION_CLIENTE,
        Intent.EVOLUCION_PROVEEDOR,
        Intent.EVOLUCION_CUENTA,
        Intent.UNKNOWN,
    })

    def resolve(self, intent: Intent) -> ResponseMode:
        if intent in self.DETERMINISTIC_INTENTS:
            return ResponseMode.DETERMINISTIC
        return ResponseMode.GENERATIVE
