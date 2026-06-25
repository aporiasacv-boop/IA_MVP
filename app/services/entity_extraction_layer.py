import re
import time
import unicodedata

from app.schemas.entities import ExtractedEntities


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


class EntityExtractionLayer:
    MONTHS: dict[str, int] = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "setiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12,
    }

    VALID_YEARS: frozenset[int] = frozenset({2024, 2025, 2026, 2027})

    PERIOD_PATTERNS: tuple[tuple[str, str], ...] = (
        (r"\bultimo mes\b", "last_month"),
        (r"\beste mes\b", "current_month"),
        (r"\bultimo ano\b", "last_year"),
        (r"\bultimo anio\b", "last_year"),
        (r"\bel ano pasado\b", "last_year"),
        (r"\bel anio pasado\b", "last_year"),
        (r"\beste ano\b", "current_year"),
        (r"\beste anio\b", "current_year"),
    )

    CLIENT_CODE_PATTERN = re.compile(r"\b(C\d{4})\b", re.IGNORECASE)
    ACCOUNT_CODE_PATTERN = re.compile(r"\b(\d{8})\b")
    YEAR_PATTERN = re.compile(r"\b(202[4-7])\b")

    def extract(
        self,
        text: str,
        *,
        alternate_text: str | None = None,
        timings: object | None = None,
    ) -> ExtractedEntities:
        started = time.perf_counter()
        combined = self._combine_texts(text, alternate_text)

        period = self._extract_period(combined)
        client_code = self._extract_client_code(combined)
        account_code = self._extract_account_code(combined)
        year = self._extract_year(combined)
        month = self._extract_month(combined)

        if timings is not None:
            timings.entity_extraction_ms = _elapsed_ms(started)

        return ExtractedEntities(
            month=month,
            year=year,
            client_code=client_code,
            account_code=account_code,
            period=period,
        )

    def _combine_texts(self, text: str, alternate_text: str | None) -> str:
        parts = [self._normalize(text)]
        if alternate_text and alternate_text.strip():
            alt = self._normalize(alternate_text)
            if alt and alt not in parts:
                parts.append(alt)
        return " ".join(parts)

    def _extract_period(self, normalized: str) -> str | None:
        for pattern, value in self.PERIOD_PATTERNS:
            if re.search(pattern, normalized):
                return value
        return None

    def _extract_client_code(self, normalized: str) -> str | None:
        match = self.CLIENT_CODE_PATTERN.search(normalized.upper())
        if match:
            return match.group(1).upper()
        return None

    def _extract_account_code(self, normalized: str) -> str | None:
        for match in self.ACCOUNT_CODE_PATTERN.finditer(normalized):
            code = match.group(1)
            if len(code) == 8:
                return code
        return None

    def _extract_year(self, normalized: str) -> int | None:
        match = self.YEAR_PATTERN.search(normalized)
        if match:
            year = int(match.group(1))
            if year in self.VALID_YEARS:
                return year
        return None

    def _extract_month(self, normalized: str) -> int | None:
        for name, number in self.MONTHS.items():
            if re.search(rf"\b{re.escape(name)}\b", normalized):
                return number
        return None

    @staticmethod
    def _normalize(text: str) -> str:
        lowered = text.lower().strip()
        decomposed = unicodedata.normalize("NFD", lowered)
        without_accents = "".join(
            char for char in decomposed if unicodedata.category(char) != "Mn"
        )
        cleaned = re.sub(r"[^\w\s]", " ", without_accents)
        return re.sub(r"\s+", " ", cleaned).strip()
