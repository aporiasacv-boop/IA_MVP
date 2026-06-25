import calendar
import re
import unicodedata
from datetime import date


class TemporalResolver:
    MONTHS = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12,
    }

    def __init__(
        self,
        fecha_minima: str,
        fecha_maxima: str,
        anios: list[int],
    ) -> None:
        self.fecha_minima = date.fromisoformat(fecha_minima)
        self.fecha_maxima = date.fromisoformat(fecha_maxima)
        self.anios = anios or [self.fecha_minima.year]

    @classmethod
    def from_metadata(cls, metadata: dict) -> "TemporalResolver":
        return cls(
            fecha_minima=metadata["fecha_minima"],
            fecha_maxima=metadata["fecha_maxima"],
            anios=metadata.get("anios", []),
        )

    def resolve(self, expression: str) -> dict[str, str] | None:
        normalized = self._normalize(expression)
        if not normalized:
            return None

        month_match = self._match_month(normalized)
        if month_match is not None:
            mes, anio = month_match
            return self._month_range(anio, mes)

        year_match = re.search(r"\b(20\d{2})\b", normalized)
        if year_match:
            anio = int(year_match.group(1))
            if anio in self.anios:
                return self._year_range(anio)

        return None

    def resolve_from_question(self, question: str) -> dict[str, str] | None:
        normalized = self._normalize(question)
        if not normalized:
            return None

        for month_name, mes in self.MONTHS.items():
            if re.search(rf"\b{month_name}\b", normalized):
                anio = self._extract_year(normalized) or self._default_year()
                if self._month_in_range(anio, mes):
                    return self._month_range(anio, mes)

        year_match = re.search(r"\b(20\d{2})\b", normalized)
        if year_match:
            anio = int(year_match.group(1))
            if anio in self.anios:
                return self._year_range(anio)

        return None

    def format_context(self, period: dict[str, str] | None) -> str:
        if period is None:
            return (
                "Referencia temporal: periodo completo del dataset "
                f"({self.fecha_minima.isoformat()} a {self.fecha_maxima.isoformat()})."
            )
        return (
            "Referencia temporal resuelta: "
            f"{period['inicio']} a {period['fin']}."
        )

    def _match_month(self, normalized: str) -> tuple[int, int] | None:
        for month_name, mes in self.MONTHS.items():
            if normalized == month_name or re.fullmatch(rf"{month_name}", normalized):
                anio = self._default_year()
                if self._month_in_range(anio, mes):
                    return mes, anio
        return None

    def _extract_year(self, normalized: str) -> int | None:
        match = re.search(r"\b(20\d{2})\b", normalized)
        if match:
            return int(match.group(1))
        return None

    def _default_year(self) -> int:
        if len(self.anios) == 1:
            return self.anios[0]
        return self.fecha_maxima.year

    def _month_in_range(self, anio: int, mes: int) -> bool:
        start = date(anio, mes, 1)
        last_day = calendar.monthrange(anio, mes)[1]
        end = date(anio, mes, last_day)
        return start >= self.fecha_minima and end <= self.fecha_maxima

    def _month_range(self, anio: int, mes: int) -> dict[str, str]:
        last_day = calendar.monthrange(anio, mes)[1]
        return {
            "inicio": date(anio, mes, 1).isoformat(),
            "fin": date(anio, mes, last_day).isoformat(),
        }

    def _year_range(self, anio: int) -> dict[str, str]:
        start = max(date(anio, 1, 1), self.fecha_minima)
        end = min(date(anio, 12, 31), self.fecha_maxima)
        return {
            "inicio": start.isoformat(),
            "fin": end.isoformat(),
        }

    @staticmethod
    def _normalize(text: str) -> str:
        lowered = text.lower().strip()
        decomposed = unicodedata.normalize("NFD", lowered)
        without_accents = "".join(
            char for char in decomposed if unicodedata.category(char) != "Mn"
        )
        cleaned = re.sub(r"[^\w\s]", " ", without_accents)
        return re.sub(r"\s+", " ", cleaned).strip()
