import pytest

from app.operational_metrics.metrics import reset_operational_finops_metrics
from app.operational_metrics.repository import reset_operational_memory_store
from app.operational_metrics.service import reset_operational_metrics_service
from app.simulation_engine.metrics import reset_simulation_engine_metrics
from app.simulation_engine.service import reset_simulation_engine_service
from app.enterprise_decision.metrics import reset_enterprise_decision_metrics
from app.enterprise_decision.service import reset_enterprise_decision_service


@pytest.fixture(autouse=True)
def reset_operational_metrics_state() -> None:
    reset_operational_memory_store()
    reset_operational_finops_metrics()
    reset_operational_metrics_service()
    reset_simulation_engine_metrics()
    reset_simulation_engine_service()
    reset_enterprise_decision_metrics()
    reset_enterprise_decision_service()
