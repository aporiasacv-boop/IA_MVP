_plan_metrics = {
    "executions_total": 0,
    "fallback_avoided_total": 0,
    "partial_executions_total": 0,
    "fallback_kept_total": 0,
}


def record_plan_execution(
    *,
    executed: bool,
    fallback_avoided: bool,
    partial_execution: bool,
) -> None:
    _plan_metrics["executions_total"] += 1
    if executed and fallback_avoided:
        _plan_metrics["fallback_avoided_total"] += 1
    if partial_execution:
        _plan_metrics["partial_executions_total"] += 1
    if not executed:
        _plan_metrics["fallback_kept_total"] += 1


def plan_executor_metrics_snapshot() -> dict:
    return dict(_plan_metrics)


def reset_plan_executor_metrics_for_tests() -> None:
    _plan_metrics["executions_total"] = 0
    _plan_metrics["fallback_avoided_total"] = 0
    _plan_metrics["partial_executions_total"] = 0
    _plan_metrics["fallback_kept_total"] = 0
