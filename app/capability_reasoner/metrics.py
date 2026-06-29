_reasoner_metrics = {
    "plans_total": 0,
    "fallback_recommended_total": 0,
    "combination_plans_total": 0,
}


def record_reasoner_metrics(*, fallback_recommended: bool, combination: bool) -> None:
    _reasoner_metrics["plans_total"] += 1
    if fallback_recommended:
        _reasoner_metrics["fallback_recommended_total"] += 1
    if combination:
        _reasoner_metrics["combination_plans_total"] += 1


def reasoner_metrics_snapshot() -> dict:
    return dict(_reasoner_metrics)


def reset_reasoner_metrics_for_tests() -> None:
    _reasoner_metrics["plans_total"] = 0
    _reasoner_metrics["fallback_recommended_total"] = 0
    _reasoner_metrics["combination_plans_total"] = 0
