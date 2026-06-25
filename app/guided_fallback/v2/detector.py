import re

from app.guided_fallback.v2.domains import DOMAIN_HINTS, BusinessDomain
from app.utils.text_normalizer import normalize_for_matching


def detect_domain(question: str) -> BusinessDomain | None:
    normalized = normalize_for_matching(question)
    if not normalized:
        return None

    matches: list[tuple[int, BusinessDomain]] = []
    for domain, hints in DOMAIN_HINTS.items():
        for hint in hints:
            if _hint_matches(hint, normalized):
                matches.append((len(hint), domain))

    if not matches:
        return None

    matches.sort(key=lambda item: (-item[0], item[1].value))
    return matches[0][1]


def _hint_matches(hint: str, normalized: str) -> bool:
    if " " in hint:
        return hint in normalized
    pattern = rf"\b{re.escape(hint)}\b"
    return re.search(pattern, normalized) is not None
