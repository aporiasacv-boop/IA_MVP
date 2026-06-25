# Observability Audit — Asistente de Inteligencia Empresarial Olnatura

**Fecha:** 2026-06-23

---

## Arquitectura de observabilidad

```
HybridChatRouter
    → PerformanceTracker.record_stage()
    → PerformanceMetricsRepository.save()
    → PostgreSQL performance_metrics

MetricsService.get_summary()
    ├── Agregación SQL (repository)
    ├── CoverageRecoveryMetricsService.snapshot()      [in-memory]
    ├── CapabilityDiscoveryV2Metrics.snapshot()        [in-memory]
    └── GuidedFallbackV2Metrics.snapshot()               [in-memory]
```

---

## Métricas persistidas (PostgreSQL)

| Campo / concepto | Registrado en | Consumido por |
|------------------|---------------|---------------|
| `handled_by` | `performance_tracker` | `/api/metrics/*`, `/api/analytics/*`, `/api/audit/*` |
| `query_type` | idem | Top queries, audit failures |
| `success` | idem | Success rates, audit overview |
| Tiempos por etapa (`intent_ms`, `planner_ms`, etc.) | idem | Performance dashboards |
| `suggested_questions_count` | idem | Adoption metrics |
| `total_ms`, `database_time_ms` | idem | Latency percentiles |

**Estado:** **ACTIVO** — núcleo de observabilidad.

---

## Métricas in-memory (no duraderas)

| Servicio | Métricas | Registro | Consumo | Riesgo |
|----------|----------|----------|---------|--------|
| `GuidedFallbackV2Metrics` | `domain_fallback_hits/misses`, `top_domains` | `guided_fallback/engine.py` | `/api/metrics/summary`, `/api/audit/report` | Se pierden al reiniciar |
| `CapabilityDiscoveryV2Metrics` | `capability_discovery_v2_responses`, length | `capability_discovery/engine.py` | `/api/metrics/summary` | Idem |
| `CoverageRecoveryMetricsService` | `coverage_recovery_hits/misses` | `hybrid_chat_router.py` | Summary + metadata respuesta | Idem |
| `ConversationMemoryService` | `memory_hits/misses` | `conversation_memory/service.py` | Parcial en summary | Idem; no thread-safe multi-worker |

---

## Endpoints de exposición

| Endpoint | Métricas expuestas | Frontend | Tests |
|----------|-------------------|----------|-------|
| `GET /api/metrics/summary` | Agregado global + v2 snapshots | Sí | Sí |
| `GET /api/metrics/top-queries` | Top preguntas | Sí | Sí |
| `GET /api/metrics/performance` | Percentiles latencia | Sí | Sí |
| `GET /api/metrics/routing` | Distribución rutas, paths | **No** | Sí |
| `GET /api/analytics/coverage` | Cobertura canales | Sí | Sí |
| `GET /api/analytics/financial` | Costos equivalentes | Sí | Sí |
| `GET /api/audit/overview` | Resumen operacional | Sí | Sí |
| `GET /api/audit/adoption` | Adopción capacidades | Sí | Sí |
| `GET /api/audit/report` | Domain fallback + gaps | **No** | 1 test |

---

## Métricas por etapa del hybrid router

Registradas vía `record_stage()` en `hybrid_chat_router.py`:

| Etapa | Identificador | Consumida |
|-------|---------------|-----------|
| Memoria conversacional | `conversation_memory` | Sí (indirecto) |
| Intent | `intent` | Sí |
| Planner | `planner` | Sí |
| Capability discovery | `capability_discovery` | Sí |
| Slot clarification | `slot_clarification` | Sí |
| Guided fallback | `guided_fallback` | Sí |
| Business pipeline | `business_pipeline` / executor | Sí |
| Legacy chat | `legacy_chat` | Sí |
| Ollama | `ollama` | Sí |

---

## Métricas legacy (chat.py)

| Mecanismo | Persistencia | Consumo |
|-----------|--------------|---------|
| `TimingCollector` | Solo en respuesta HTTP (`ChatTimings`) | Frontend `TechnicalDetails` cuando legacy |
| `PromptAudit` | En metadata de respuesta | No persistido en DB |

---

## Duplicaciones detectadas

| Métrica | Ubicación 1 | Ubicación 2 | Observación |
|---------|-------------|-------------|-------------|
| Top queries | `/api/metrics/top-queries` | `/api/analytics/top-queries` | Misma fuente `performance_metrics`, DTOs distintos |
| Performance latencia | `/api/metrics/performance` | `/api/analytics/performance` | Agregaciones similares |
| Cobertura | `/api/analytics/coverage` | `/api/audit/overview` | Perspectivas distintas (analytics vs audit) |
| Domain fallback | In-memory v2 | `/api/audit/report` | No en UI principal |

---

## Métricas nunca consumidas (o sin consumidor UI)

| Métrica / endpoint | Estado |
|--------------------|--------|
| `GET /api/metrics/routing` | Backend + tests; **sin frontend** |
| `RoutingMetricsResponse` | Schema sin cliente React |
| `GET /api/audit/report` | Solo test integración |
| Snapshots in-memory tras restart | **Vacíos** hasta nuevo tráfico |

---

## Métricas obsoletas / candidatas a consolidación

| Elemento | Razón |
|----------|-------|
| KPIs `/api/kpis*` | Paralelos a observabilidad híbrida; sin UI |
| `TimingCollector` sin persistencia | No alimenta dashboards cuando solo hybrid |
| Contadores v1 en guided_fallback si v2 cubre dominio | Coexistencia v1/v2 |

---

## Health checks internos (no métricas HTTP)

Módulos con validación de salud en tests:
- `capability_discovery/health.py`
- `coverage_recovery/health.py`
- `suggested_questions/health.py`
- `business_analytics` health tests
- `operational_audit/health.py`

---

## Resumen

| Categoría | Cantidad |
|-----------|----------|
| Fuentes de métricas | 2 (PostgreSQL + in-memory) |
| Endpoints exposición | 12+ |
| Endpoints sin UI | 2 (`routing`, `audit/report`) |
| Duplicaciones funcionales | 3 pares |
| Métricas volátiles (in-memory) | 4 servicios |
