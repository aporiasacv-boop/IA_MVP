# Observability v1

## Objetivo

Primera capa de **observabilidad y métricas de rendimiento** del Asistente de Inteligencia Empresarial Olnatura.

Mide, registra y expone métricas del pipeline híbrido sin modificar reglas de negocio ni optimizar componentes. Genera evidencia para decisiones futuras de arquitectura y performance.

## Arquitectura

```
POST /api/chat/hybrid
        │
        ▼
HybridChatRouter + PerformanceTracker
        │
        ├─ business_pipeline
        │     ├─ SemanticIntentBuilder (operation, entity, intent)
        │     ├─ BusinessQueryPlanner
        │     ├─ BusinessQueryExecutor
        │     └─ Response Engine v1
        │
        └─ legacy_chat (Intent Router / Ollama)
        │
        ▼
performance_metrics (PostgreSQL)
        │
        ▼
GET /api/metrics/*
```

### Componentes

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Modelo | `app/observability/performance_metrics.py` | `PerformanceMetrics`, collector |
| Tracker | `app/observability/performance_tracker.py` | Medición y persistencia |
| Repositorio | `app/observability/metrics_repository.py` | ORM + agregados SQL |
| DB timing | `app/observability/db_timing.py` | Acumulador `database_time_ms` |
| API | `app/api/routes/metrics.py` | Endpoints de consulta |
| Migración | `alembic/versions/005_create_performance_metrics.py` | Tabla PostgreSQL |

## Métricas capturadas

| Campo | Significado |
|-------|-------------|
| `request_id` | Identificador único del request |
| `question` | Pregunta original |
| `handled_by` | `business_pipeline` o `legacy_chat` |
| `operation_time_ms` | Tiempo del Operation Resolver |
| `entity_time_ms` | Tiempo del Entity Resolver |
| `intent_time_ms` | Tiempo total de Semantic Intent Builder |
| `planner_time_ms` | Tiempo del Business Query Planner |
| `executor_time_ms` | Tiempo del Business Query Executor |
| `database_time_ms` | Suma de consultas PostgreSQL en repositories |
| `response_time_ms` | Tiempo del Response Engine v1 |
| `legacy_chat_time_ms` | Tiempo del flujo legacy completo |
| `ollama_time_ms` | Tiempo LLM reportado por `ChatTimings.llm_ms` |
| `total_time_ms` | Tiempo total del request híbrido |
| `query_type` | Tipo de consulta planificada |
| `success` | Éxito de la respuesta final |
| `created_at` | Timestamp UTC |

## Interpretación

- **`intent_time_ms` alto** — revisar catálogos o complejidad de la pregunta en resolvers.
- **`database_time_ms` alto** — revisar índices del Data Mart o volumen de datos.
- **`legacy_chat` dominante** — ampliar reglas del Query Planner.
- **`ollama_time_ms` alto** — esperado en preguntas abiertas; no afecta pipeline determinístico.
- **P95/P99 elevados** — identificar outliers con `/api/metrics/performance` y `docs/performance_queries.sql`.

## Endpoints

```
GET /api/metrics/summary
GET /api/metrics/top-queries?limit=10
GET /api/metrics/performance
```

## Instrumentación

- **HybridChatRouter** — etapas del pipeline y legacy.
- **SemanticIntentBuilder** — `operation_time_ms` y `entity_time_ms` cuando hay tracker activo.
- **Repositories** (`cliente_repository`, `proveedor_repository`) — `track_database_call()` sin modificar SQL.

## Restricciones

- No OpenTelemetry, Prometheus ni Grafana en este sprint.
- No optimización de componentes.
- Métricas solo se persisten en `POST /api/chat/hybrid` (no en `/api/chat` legacy directo).

## Roadmap futuro

1. OpenTelemetry traces distribuidos.
2. Export Prometheus + dashboard Grafana.
3. Alertas sobre P95 y tasa de `UNSUPPORTED`.
4. Métricas en `/api/chat` principal al promover el router híbrido.
5. Correlación `request_id` con logs estructurados.

## Pruebas

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m pytest tests/test_observability.py -v --cov=app.observability --cov-report=term-missing
.\.venv\Scripts\python.exe -m pytest tests/integration/test_observability_integration.py -v -m integration
```

Cobertura mínima: **90%** en `app/observability`.
