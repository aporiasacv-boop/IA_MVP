import json
import re

from app.executive_advisor.constants import ADVISOR_MAX_ITEMS
from app.executive_advisor.schemas import ExecutiveAgenda, ExecutiveAgendaItem


def parse_advisor_response(text: str) -> ExecutiveAgenda | None:
    cleaned = text.strip()
    if not cleaned:
        return None

    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        payload = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    greeting = str(payload.get("greeting", "")).strip()
    raw_items = payload.get("items")
    if not greeting or not isinstance(raw_items, list):
        return None

    items: list[ExecutiveAgendaItem] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        try:
            item = ExecutiveAgendaItem.model_validate(raw)
        except Exception:
            continue
        if item.title.strip() and item.suggested_query.strip():
            items.append(item)

    if not items:
        return None

    return ExecutiveAgenda(greeting=greeting, items=items[:ADVISOR_MAX_ITEMS])
