import json
import re

from app.executive_insight.schemas import ExecutiveInsightPayload


def parse_insight_response(text: str) -> ExecutiveInsightPayload | None:
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

    return ExecutiveInsightPayload.model_validate(payload)
