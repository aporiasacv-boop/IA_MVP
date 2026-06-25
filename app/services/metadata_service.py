import calendar
from datetime import date

from app.repositories.metadata_repository import MetadataRepository


class MetadataService:
    def __init__(self, repository: MetadataRepository) -> None:
        self.repository = repository

    def get_dataset_summary(self) -> dict:
        raw = self.repository.fetch_dataset_metadata()
        min_anio, min_mes = self._decode_period(raw["periodo_min"])
        max_anio, max_mes = self._decode_period(raw["periodo_max"])
        return {
            "fecha_minima": self._first_day(min_anio, min_mes).isoformat(),
            "fecha_maxima": self._last_day(max_anio, max_mes).isoformat(),
            "registros": int(raw["total_registros"]),
            "clientes": int(raw["total_clientes"]),
            "proveedores": int(raw["total_proveedores"]),
            "cuentas": int(raw["total_cuentas"]),
            "anios": [int(year) for year in raw["anios_disponibles"]],
            "meses": int(raw["total_meses"]),
        }

    def get_prompt_context(self) -> str:
        summary = self.get_dataset_summary()
        anios = ", ".join(str(year) for year in summary["anios"])
        return (
            "Contexto del dataset:\n"
            f"Periodo disponible: {summary['fecha_minima']} a {summary['fecha_maxima']}\n"
            f"Registros: {summary['registros']}\n"
            f"Clientes: {summary['clientes']}\n"
            f"Proveedores: {summary['proveedores']}\n"
            f"Cuentas: {summary['cuentas']}\n"
            f"Anios disponibles: {anios}\n"
            f"Meses disponibles: {summary['meses']}"
        )

    @staticmethod
    def _decode_period(period_key: int | None) -> tuple[int, int]:
        if not period_key:
            return 1, 1
        return int(period_key // 100), int(period_key % 100)

    @staticmethod
    def _first_day(anio: int, mes: int) -> date:
        return date(anio, mes, 1)

    @staticmethod
    def _last_day(anio: int, mes: int) -> date:
        last_day = calendar.monthrange(anio, mes)[1]
        return date(anio, mes, last_day)
