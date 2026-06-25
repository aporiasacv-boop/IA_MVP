"""Métricas legacy: delegan en Enterprise Knowledge Service."""

from app.enterprise_knowledge_service.metrics import (
    get_enterprise_knowledge_metrics,
    reset_enterprise_knowledge_metrics,
)


class BusinessKnowledgeRuntimeMetrics:
  @property
  def hits(self) -> int:
      return get_enterprise_knowledge_metrics().hits

  @property
  def misses(self) -> int:
      return get_enterprise_knowledge_metrics().misses

  @property
  def cache_hits(self) -> int:
      return get_enterprise_knowledge_metrics().cache_hits

  @property
  def reload_time_ms(self) -> float:
      return get_enterprise_knowledge_metrics().reload_time_ms

  @property
  def last_refresh(self):
      return get_enterprise_knowledge_metrics().last_refresh

  def record_hit(self) -> None:
      get_enterprise_knowledge_metrics().record_hit()

  def record_miss(self) -> None:
      get_enterprise_knowledge_metrics().record_miss()

  def record_cache_hit(self) -> None:
      get_enterprise_knowledge_metrics().record_cache_hit()

  def record_reload(self, elapsed_ms: float) -> None:
      get_enterprise_knowledge_metrics().record_reload(elapsed_ms)

  def snapshot(self) -> dict:
      return get_enterprise_knowledge_metrics().snapshot()


_metrics_adapter = BusinessKnowledgeRuntimeMetrics()


def get_business_knowledge_metrics() -> BusinessKnowledgeRuntimeMetrics:
    return _metrics_adapter


def reset_business_knowledge_metrics() -> None:
    reset_enterprise_knowledge_metrics()
