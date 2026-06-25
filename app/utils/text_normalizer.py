import re
import unicodedata


def normalize_text(text: str) -> str:
    """Convierte a minusculas, elimina acentos y espacios duplicados."""
    lowered = text.lower().strip()
    decomposed = unicodedata.normalize("NFD", lowered)
    without_accents = "".join(
        char for char in decomposed if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"\s+", " ", without_accents).strip()


def normalize_for_matching(text: str) -> str:
    """Normaliza texto y elimina puntuacion para coincidencia por terminos."""
    cleaned = re.sub(r"[^\w\s]", " ", normalize_text(text))
    return re.sub(r"\s+", " ", cleaned).strip()
