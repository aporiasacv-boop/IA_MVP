import re

from app.domain.entity_catalog import MONTH_NAMES
from app.slot_clarification.slots import ClarificationSlot
from app.utils.text_normalizer import normalize_for_matching, normalize_text

_CLIENT_CODE_PATTERN = re.compile(r"^\s*C\d+\s*$", re.IGNORECASE)
_PROVIDER_CODE_PATTERN = re.compile(r"^\s*P\d+\s*$", re.IGNORECASE)
_ACCOUNT_CODE_PATTERN = re.compile(r"^\s*[A-Za-z0-9]*\d[A-Za-z0-9]+\s*$")
_MONTH_INT_PATTERN = re.compile(r"^\s*(1[0-2]|[1-9])\s*$")

MONTH_TO_INT: dict[str, int] = {
    normalize_text(name): index
    for index, name in enumerate(MONTH_NAMES, start=1)
}


def parse_slot_value(message: str, slot: str) -> str | int | None:
    slot_enum = ClarificationSlot(slot)
    trimmed = message.strip()
    if not trimmed:
        return None

    if slot_enum == ClarificationSlot.CLIENTE_CODIGO:
        match = _CLIENT_CODE_PATTERN.match(trimmed)
        return match.group().strip().upper() if match else None

    if slot_enum == ClarificationSlot.PROVEEDOR_CODIGO:
        match = _PROVIDER_CODE_PATTERN.match(trimmed)
        return match.group().strip().upper() if match else None

    if slot_enum == ClarificationSlot.CUENTA_CODIGO:
        if _ACCOUNT_CODE_PATTERN.match(trimmed) and len(trimmed) >= 5:
            return trimmed.upper()
        return None

    if slot_enum == ClarificationSlot.MES:
        if _MONTH_INT_PATTERN.match(trimmed):
            return int(trimmed.strip())
        month_key = normalize_text(trimmed)
        return MONTH_TO_INT.get(month_key)

    if slot_enum == ClarificationSlot.ANIO:
        year_match = re.match(r"^\s*((?:19|20)\d{2})\s*$", trimmed)
        return int(year_match.group(1)) if year_match else None

    return None
