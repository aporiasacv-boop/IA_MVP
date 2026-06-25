from typing import Any

from app.services.intent_router import Intent


class LlmContextOptimizer:
    MINIMAL_METADATA_KEYS = ("fecha_minima", "fecha_maxima", "registros")

    INTENT_SOURCES: dict[str, list[str]] = {
        Intent.TOP_CLIENTES.value: ["TOP_CLIENTES", "METADATA"],
        Intent.TOP_PROVEEDORES.value: ["TOP_PROVEEDORES", "METADATA"],
        Intent.TOP_CUENTAS.value: ["TOP_CUENTAS", "METADATA"],
        Intent.MONTH_ANALYSIS.value: ["METADATA", "RESUMEN_MENSUAL", "INSIGHTS"],
        Intent.YEAR_SUMMARY.value: [
            "METADATA",
            "KPIS_EJECUTIVOS",
            "INSIGHTS",
            "TOP_CLIENTES",
            "TOP_PROVEEDORES",
        ],
        Intent.EXECUTIVE_INSIGHTS.value: ["INSIGHTS", "KPIS_EJECUTIVOS", "METADATA"],
        Intent.BUSINESS_CONCENTRATION.value: [
            "INSIGHTS",
            "TOP_CLIENTES",
            "KPIS_EJECUTIVOS",
            "METADATA",
        ],
    }

    def optimize(
        self,
        intent: str,
        data: Any,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, list[str]]:
        minimal_metadata = self._minimal_metadata(data, metadata)
        sources = self.INTENT_SOURCES.get(intent, [])

        if intent == Intent.TOP_CLIENTES.value:
            return self._wrap(minimal_metadata, top_cliente=self._first_item(data)), sources

        if intent == Intent.TOP_PROVEEDORES.value:
            return (
                self._wrap(minimal_metadata, top_proveedor=self._first_item(data)),
                sources,
            )

        if intent == Intent.TOP_CUENTAS.value:
            return self._wrap(minimal_metadata, top_cuenta=self._first_item(data)), sources

        if intent == Intent.MONTH_ANALYSIS.value and isinstance(data, dict):
            return (
                {
                    "metadata": minimal_metadata,
                    "temporal": data.get("temporal"),
                    "mes": data.get("mes"),
                    "promedio_mensual": data.get("promedio_mensual"),
                    "insights": data.get("insights"),
                },
                sources,
            )

        if intent == Intent.YEAR_SUMMARY.value and isinstance(data, dict):
            return (
                {
                    "metadata": minimal_metadata,
                    "temporal": data.get("temporal"),
                    "kpis_ejecutivos": data.get("kpis_ejecutivos"),
                    "insights": data.get("insights"),
                    "top_clientes": self._top_n(data.get("top_clientes"), 5),
                    "top_proveedores": self._top_n(data.get("top_proveedores"), 5),
                },
                sources,
            )

        if intent == Intent.EXECUTIVE_INSIGHTS.value and isinstance(data, dict):
            return (
                {
                    "metadata": minimal_metadata,
                    "temporal": data.get("temporal"),
                    "insights": data.get("insights"),
                    "kpis_ejecutivos": data.get("kpis_ejecutivos"),
                },
                sources,
            )

        if intent == Intent.BUSINESS_CONCENTRATION.value and isinstance(data, dict):
            kpis = data.get("kpis_ejecutivos") or {}
            return (
                {
                    "metadata": minimal_metadata,
                    "temporal": data.get("temporal"),
                    "concentracion": data.get("insights"),
                    "top_clientes": self._top_n(data.get("top_clientes"), 5),
                    "participacion_top_5": kpis.get("top_5_clientes_participacion"),
                    "participacion_top_10": kpis.get("top_10_clientes_participacion"),
                },
                sources,
            )

        if sources:
            return self._wrap(minimal_metadata, payload=data), sources
        return self._wrap(minimal_metadata, payload=data), self._infer_sources(intent)

    @classmethod
    def _minimal_metadata(
        cls,
        data: Any,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if isinstance(data, dict) and isinstance(data.get("metadata"), dict):
            source = data["metadata"]
        elif metadata:
            source = metadata
        else:
            return {}
        return {key: source[key] for key in cls.MINIMAL_METADATA_KEYS if key in source}

    @staticmethod
    def _wrap(metadata: dict[str, Any], **payload: Any) -> dict[str, Any]:
        result = {"metadata": metadata}
        result.update(payload)
        return result

    @staticmethod
    def _first_item(data: Any) -> dict[str, Any] | None:
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return data[0]
        return None

    @staticmethod
    def _top_n(data: Any, limit: int) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return [item for item in data[:limit] if isinstance(item, dict)]
        return []

    @staticmethod
    def _infer_sources(intent: str) -> list[str]:
        return [intent] if intent else []
