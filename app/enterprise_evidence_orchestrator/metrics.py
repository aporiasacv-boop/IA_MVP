_orchestrator_metrics = {
    "packages_total": 0,
    "partial_packages_total": 0,
    "skipped_total": 0,
}


def record_orchestration(
    *,
    built_package: bool,
    partial: bool,
) -> None:
    if not built_package:
        _orchestrator_metrics["skipped_total"] += 1
        return
    _orchestrator_metrics["packages_total"] += 1
    if partial:
        _orchestrator_metrics["partial_packages_total"] += 1


def orchestrator_metrics_snapshot() -> dict:
    return dict(_orchestrator_metrics)


def reset_orchestrator_metrics_for_tests() -> None:
    _orchestrator_metrics["packages_total"] = 0
    _orchestrator_metrics["partial_packages_total"] = 0
    _orchestrator_metrics["skipped_total"] = 0
