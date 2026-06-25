def pct(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((count / total) * 100, 2)


def coverage_score(*, deterministic_count: int, total: int, success_rate: float) -> float:
    """Cobertura operacional: proporción determinística × éxito."""
    if total <= 0:
        return 0.0
    deterministic_rate = deterministic_count / total
    score = deterministic_rate * success_rate * 100
    return round(min(max(score, 0.0), 100.0), 2)


def coverage_gap_score(*, legacy_count: int, fallback_count: int, total: int) -> float:
    """
    Coverage Gap Score (0–100):

        coverage_gap_score = ((legacy_chat + guided_fallback) / total_requests) × 100

    Mide qué proporción del tráfico no fue resuelta directamente por el pipeline
    empresarial y terminó en orientación (guided_fallback) o IA (legacy_chat).
    """
    if total <= 0:
        return 0.0
    gap_rate = (legacy_count + fallback_count) / total
    return round(min(max(gap_rate * 100, 0.0), 100.0), 2)
