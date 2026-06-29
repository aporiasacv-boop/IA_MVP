import json
import re

from app.reasoning_engine.constants import VALID_ROUTES
from app.reasoning_engine.schemas import ReasoningDecision


def parse_reasoning_response(raw_text: str) -> ReasoningDecision:
    payload = _extract_json_object(raw_text)
    intent = str(payload.get("intent", "unknown")).strip()
    confidence = _clamp_confidence(payload.get("confidence", 0.0))
    route = str(
        payload.get("recommended_route") or payload.get("route") or "unknown"
    ).strip()
    explanation = str(payload.get("explanation", "")).strip()

    if route not in VALID_ROUTES:
        raise ValueError(f"Ruta no válida: {route}")

    if not explanation:
        raise ValueError("Explicación vacía")

    return ReasoningDecision(
        intent=intent,
        confidence=confidence,
        recommended_route=route,
        explanation=explanation,
    )


def _extract_json_object(raw_text: str) -> dict:
    text = raw_text.strip()
    if not text:
        raise ValueError("Respuesta vacía")

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match is None:
        raise ValueError("JSON no encontrado")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("JSON inválido")
    return parsed


def _clamp_confidence(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))
