_reasoning_v2_metrics = {
    "generated_total": 0,
    "skipped_total": 0,
    "fallback_total": 0,
}


def record_reasoning_v2(
    *,
    generated: bool,
    skipped: bool = False,
    fallback: bool = False,
) -> None:
    if skipped:
        _reasoning_v2_metrics["skipped_total"] += 1
        return
    if generated:
        _reasoning_v2_metrics["generated_total"] += 1
    if fallback:
        _reasoning_v2_metrics["fallback_total"] += 1


def reasoning_v2_metrics_snapshot() -> dict:
    return dict(_reasoning_v2_metrics)


def reset_reasoning_v2_metrics_for_tests() -> None:
    _reasoning_v2_metrics["generated_total"] = 0
    _reasoning_v2_metrics["skipped_total"] = 0
    _reasoning_v2_metrics["fallback_total"] = 0
