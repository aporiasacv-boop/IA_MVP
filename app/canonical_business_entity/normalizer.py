import re
import unicodedata
from difflib import SequenceMatcher

RFC_PATTERN = re.compile(r"[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}", re.IGNORECASE)
RFC_PREFIX_PATTERN = re.compile(r"^[A-Z&Ñ]{3,4}\d{6,}", re.IGNORECASE)

LEGAL_SUFFIXES = (
    "SA DE CV",
    "S.A. DE C.V.",
    "S DE RL DE CV",
    "S DE RL",
    "S.A.",
    "S.C.",
    "SPR",
    "AC",
    "LLC",
    "INC",
)

STOPWORDS = frozenset({
    "DE",
    "LA",
    "EL",
    "LOS",
    "LAS",
    "Y",
    "EN",
    "DEL",
    "SA",
    "CV",
    "RL",
    "SC",
    "MX",
    "MEXICO",
    "NUEVA",
    "NUEVO",
})


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_organization_name(name: str) -> str:
    upper = strip_accents(name.upper().strip())
    for suffix in LEGAL_SUFFIXES:
        upper = upper.replace(suffix.upper(), " ")
    upper = re.sub(r"[^A-Z0-9&Ñ ]+", " ", upper)
    return re.sub(r"\s+", " ", upper).strip()


def extract_rfc(code: str, name: str) -> str | None:
    for candidate in (code, name):
        upper = candidate.upper().strip()
        match = RFC_PATTERN.search(upper)
        if match:
            return match.group(0).upper()
        prefix = RFC_PREFIX_PATTERN.match(upper)
        if prefix:
            return prefix.group(0).upper()
    return None


def significant_tokens(normalized_name: str) -> set[str]:
    raw_tokens = [
        token
        for token in normalized_name.split()
        if len(token) >= 3 and token not in STOPWORDS
    ]
    tokens = set(raw_tokens)
    compact = "".join(
        token for token in normalized_name.split() if token not in STOPWORDS and len(token) >= 2
    )
    if len(compact) >= 5:
        tokens.add(compact)
    return tokens


def token_overlap_score(left: str, right: str) -> float:
    left_tokens = significant_tokens(left)
    right_tokens = significant_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = left_tokens & right_tokens
    union = left_tokens | right_tokens
    return len(intersection) / len(union)


def fuzzy_name_score(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def brand_tokens(normalized_name: str) -> set[str]:
    tokens = significant_tokens(normalized_name)
    return {token for token in tokens if len(token) >= 5}


def brand_token_score(left: str, right: str) -> float:
    left_brands = brand_tokens(left)
    right_brands = brand_tokens(right)
    if not left_brands or not right_brands:
        return 0.0
    if left_brands & right_brands:
        return 0.88
    return 0.0
