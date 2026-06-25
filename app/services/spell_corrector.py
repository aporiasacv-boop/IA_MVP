import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SpellCorrectionResult:
    text: str
    corrections_applied: list[str] = field(default_factory=list)


class SpellCorrector:
    ABBREVIATIONS: dict[str, str] = {
        "q": "que",
        "ke": "que",
        "k": "que",
        "xq": "porque",
        "pq": "porque",
        "pa": "para",
    }

    WORD_CORRECTIONS: dict[str, str] = {
        "informasion": "información",
        "infomacion": "información",
        "informacion": "información",
        "clinte": "cliente",
        "clente": "cliente",
        "cleinte": "cliente",
        "provedor": "proveedor",
        "proovedor": "proveedor",
        "tines": "tienes",
        "conoses": "conoces",
        "asta": "hasta",
        "actualisado": "actualizado",
        "hallasgos": "hallazgos",
        "junoo": "junio",
        "juno": "junio",
        "junioo": "junio",
        "diciemre": "diciembre",
        "diciembr": "diciembre",
        "insigths": "insights",
        "ejecutibo": "ejecutivo",
        "concentrasion": "concentración",
        "concentracion": "concentración",
    }

    PHRASE_CORRECTIONS: dict[str, str] = {
        "que informasion tienes": "qué información tienes",
        "que infomacion tienes": "qué información tienes",
        "q informacion tienes": "qué información tienes",
        "ke informacion tienes": "qué información tienes",
        "k informacion tienes": "qué información tienes",
        "compra mas": "compra más",
        "vende mas": "vende más",
        "mueve mas": "mueve más",
    }

    def correct(self, text: str) -> SpellCorrectionResult:
        normalized = text.strip()
        corrections: list[str] = []
        lower_text = normalized.lower()

        for wrong, right in self.PHRASE_CORRECTIONS.items():
            if wrong in lower_text:
                pattern = re.compile(re.escape(wrong), re.IGNORECASE)
                normalized = pattern.sub(right, normalized)
                corrections.append(f"{wrong} -> {right}")
                lower_text = normalized.lower()

        parts = re.findall(r"\S+", normalized)
        fixed_parts: list[str] = []
        for part in parts:
            match = re.match(r"^([^\w]*)([\w']+)([^\w]*)$", part, flags=re.UNICODE)
            if not match:
                fixed_parts.append(part)
                continue
            prefix, word, suffix = match.groups()
            lower = word.lower()
            expanded = self.ABBREVIATIONS.get(lower)
            if expanded is not None:
                corrections.append(f"{lower} -> {expanded}")
                word = self._preserve_case(word, expanded)
                lower = word.lower()
            if lower in self.WORD_CORRECTIONS:
                fixed = self.WORD_CORRECTIONS[lower]
                if lower != self._ascii_key(fixed):
                    corrections.append(f"{lower} -> {fixed}")
                word = self._preserve_case(word, fixed)
            fixed_parts.append(f"{prefix}{word}{suffix}")

        return SpellCorrectionResult(" ".join(fixed_parts), corrections)

    @staticmethod
    def _ascii_key(value: str) -> str:
        return (
            value.lower()
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )

    @staticmethod
    def _preserve_case(original: str, fixed: str) -> str:
        if original.isupper():
            return fixed.upper()
        if original[0].isupper():
            return fixed.capitalize()
        return fixed.lower()

    def register_word(self, wrong: str, right: str) -> None:
        self.WORD_CORRECTIONS[wrong.lower()] = right

    def register_phrase(self, wrong: str, right: str) -> None:
        self.PHRASE_CORRECTIONS[wrong.lower()] = right

    def register_abbreviation(self, wrong: str, right: str) -> None:
        self.ABBREVIATIONS[wrong.lower()] = right
