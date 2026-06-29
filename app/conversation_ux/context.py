from dataclasses import dataclass
from collections.abc import Callable


@dataclass(frozen=True)
class DatasetSnapshot:
    registros: int | None = None
    clientes: int | None = None
    proveedores: int | None = None
    cuentas: int | None = None
    fecha_minima: str | None = None
    fecha_maxima: str | None = None

    @classmethod
    def empty(cls) -> "DatasetSnapshot":
        return cls()

    @classmethod
    def from_mapping(cls, data: dict) -> "DatasetSnapshot":
        return cls(
            registros=_optional_int(data.get("registros")),
            clientes=_optional_int(data.get("clientes")),
            proveedores=_optional_int(data.get("proveedores")),
            cuentas=_optional_int(data.get("cuentas")),
            fecha_minima=_optional_str(data.get("fecha_minima")),
            fecha_maxima=_optional_str(data.get("fecha_maxima")),
        )

    @property
    def has_counts(self) -> bool:
        return any(
            value is not None
            for value in (self.registros, self.clientes, self.proveedores, self.cuentas)
        )

    @property
    def period_label(self) -> str | None:
        if self.fecha_minima and self.fecha_maxima:
            return f"{self.fecha_minima} a {self.fecha_maxima}"
        return None


DatasetSummaryProvider = Callable[[], dict]


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def resolve_dataset_snapshot(provider: DatasetSummaryProvider | None) -> DatasetSnapshot:
    if provider is None:
        return DatasetSnapshot.empty()
    try:
        return DatasetSnapshot.from_mapping(provider())
    except Exception:
        return DatasetSnapshot.empty()
