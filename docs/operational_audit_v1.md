# Operational Reality Audit v1

Capa de **solo lectura** sobre `performance_metrics` del Hybrid Router. No modifica pipeline, planner, executor, memory ni response engine.

## Objetivo

Transformar telemetría en decisiones de producto: medir qué parte del tráfico queda cubierta por rutas determinísticas vs. gaps (`legacy_chat`, `guided_fallback`).

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/audit/overview` | Resumen global y scores |
| GET | `/api/audit/coverage-gaps` | Preguntas en legacy/fallback agrupadas |
| GET | `/api/audit/coverage-gaps/export?format=json\|csv` | Export de gaps |
| GET | `/api/audit/top-routes` | Rutas más frecuentes |
| GET | `/api/audit/top-failures` | Preguntas fallidas |
| GET | `/api/audit/adoption` | Uso de capacidades existentes |

## Métricas

### Overview

- **total_requests / total_successes / total_failures**: conteos desde `performance_metrics`.
- **business_pipeline_pct, memory_pct, clarification_pct, capability_pct, fallback_pct, legacy_pct**: `(count_route / total_requests) × 100`.
- **coverage_score** (0–100):

  ```
  deterministic_count = business_pipeline + slot_clarification
                        + conversation_memory + capability_discovery
                        + guided_fallback
  coverage_score = (deterministic_count / total_requests) × success_rate × 100
  ```

  Mide cobertura operacional ponderada por tasa de éxito.

- **coverage_gap_score** (0–100):

  ```
  coverage_gap_score = ((legacy_chat + guided_fallback) / total_requests) × 100
  ```

  Proporción del tráfico que no resolvió el pipeline empresarial directamente y terminó en orientación o IA legacy.

### Coverage Gaps

Preguntas agrupadas por `(question, handled_by)` donde `handled_by ∈ {legacy_chat, guided_fallback}`.

### Top Failures

Preguntas con `success = false`, agrupadas por frecuencia.

### Adoption

- **suggested_questions_usage**: requests con `suggested_questions_count > 0`
- **conversation_memory_usage**: `handled_by = conversation_memory`
- **slot_clarification_usage**: `handled_by = slot_clarification`
- **capability_discovery_usage**: `handled_by = capability_discovery`

## Health checks

`OperationalAuditService.validate_health()` verifica:

1. Métricas no negativas
2. `total_successes + total_failures == total_requests`
3. Suma de % por ruta ≈ 100 (tolerancia 0.5 pp)
4. `coverage_score` y `coverage_gap_score` en [0, 100]

## Interpretación

| Señal | Lectura |
|-------|---------|
| **coverage_gap_score alto** (>25%) | Mucho tráfico en fallback/legacy; priorizar nuevos query types o mejoras de discovery |
| **legacy_pct alto** | Dependencia de IA generativa; revisar gaps temáticos |
| **fallback_pct alto** | Usuarios no encuentran respuesta estructurada; mejorar clarificación o documentación de capacidades |
| **coverage_score bajo** con **success_rate alto** | Rutas determinísticas poco usadas aunque funcionan bien |
| **Adoption bajo en capability_discovery** | Preguntas definicionales van a legacy; reforzar discovery |

## Ejemplos

### Ejemplo 1 — Overview

```json
{
  "total_requests": 1000,
  "coverage_gap_score": 25.0,
  "coverage_score": 82.8,
  "legacy_pct": 10.0,
  "fallback_pct": 15.0
}
```

→ 25% del tráfico es gap. Objetivo de sprint: reducir 5 pp analizando top gaps.

### Ejemplo 2 — Coverage gap export

```csv
question,count,route
¿Cuánto vendimos ayer?,42,legacy_chat
¿Qué puedes hacer?,18,guided_fallback
```

→ "vendimos" sugiere query type de ventas; "qué puedes hacer" sugiere capability discovery.

## Cómo usar Operational Audit para decidir próximos sprints

1. **Exportar Coverage Gaps** (CSV/JSON) cada fin de sprint.
2. **Agrupar por tema** (ventas, inventario, definiciones, ayuda).
3. **Priorizar por count × impacto de negocio**.

### Reglas heurísticas

| Patrón en gaps | Acción de roadmap |
|----------------|-------------------|
| ≥40% de gaps contienen "ventas" / "facturación" | Crear query types de ventas en business pipeline |
| ≥30% de legacy son preguntas definicionales ("qué es", "cómo funciona") | Mejorar **Capability Discovery** (no nuevos query types) |
| Alto **fallback_pct** + bajo **clarification_pct** | Revisar **Slot Clarification** y slots faltantes |
| **suggested_questions_usage** bajo tras respuestas exitosas | Ajustar reglas de **Suggested Questions** (solo configuración existente) |
| **top_failures** concentrados en una ruta | Investigar observabilidad de esa ruta (executor/planner) — sin cambiar código en audit |

### Flujo recomendado

```
GET /api/audit/overview → baseline
GET /api/audit/coverage-gaps → backlog temático
GET /api/audit/top-failures → bugs / datos
GET /api/audit/adoption → madurez de capacidades
```

Repetir tras cada release y comparar `coverage_gap_score` sprint a sprint.

## Frontend

Ruta: `/audit` — pestaña **Operational Audit** en el sidebar.

Secciones: Overview, Coverage Gaps (export JSON/CSV), Top Failures, Top Routes, Adoption.

## Restricciones v1

- No agrega query types, ConceptSet ni capacidades conversacionales nuevas.
- Solo lectura sobre telemetría existente.
- Módulo: `app/operational_audit/`
