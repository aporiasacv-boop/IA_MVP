_planner_metrics = {
    "plans_total": 0,
    "multi_evidence_plans": 0,
    "single_evidence_plans": 0,
}


def record_evidence_plan(*, evidence_count: int) -> None:
    _planner_metrics["plans_total"] += 1
    if evidence_count > 1:
        _planner_metrics["multi_evidence_plans"] += 1
    else:
        _planner_metrics["single_evidence_plans"] += 1


def evidence_planner_metrics_snapshot() -> dict:
    return dict(_planner_metrics)


def reset_evidence_planner_metrics_for_tests() -> None:
    _planner_metrics["plans_total"] = 0
    _planner_metrics["multi_evidence_plans"] = 0
    _planner_metrics["single_evidence_plans"] = 0
