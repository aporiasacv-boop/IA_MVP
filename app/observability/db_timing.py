import time
from collections.abc import Callable
from typing import TypeVar

from app.observability.performance_metrics import add_database_time, elapsed_ms

T = TypeVar("T")


def track_database_call(operation: Callable[[], T]) -> T:
    started_at = time.perf_counter()
    try:
        return operation()
    finally:
        add_database_time(elapsed_ms(started_at))
