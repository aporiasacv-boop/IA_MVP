# Endpoint Audit — Asistente de Inteligencia Empresarial Olnatura

**Fecha:** 2026-06-23  
**Total endpoints registrados:** 39  
**Fuente:** `app/main.py` + routers en `app/api/routes/`

---

## Leyenda de clasificación

| Clasificación | Criterio |
|---------------|----------|
| **PRODUCCION** | Consumido por frontend React o flujo principal hybrid en operación normal |
| **EXPERIMENTAL** | Expuesto para desarrollo/diagnóstico; tests pero no UI |
| **NO UTILIZADO** | Sin consumidor frontend; solo scripts o sin referencias |

---

## Inventario completo

### Infraestructura

| Método | Path | Clasificación | Frontend | Tests | Backend interno |
|--------|------|---------------|----------|-------|-----------------|
| GET | `/health` | PRODUCCION | No | Sí | — |
| GET | `/version` | PRODUCCION | No | Sí | — |

### Upload

| Método | Path | Clasificación | Frontend | Tests | Scripts |
|--------|------|---------------|----------|-------|---------|
| POST | `/upload` | NO UTILIZADO | No | No | — |

### Chat

| Método | Path | Clasificación | Frontend | Tests | Notas |
|--------|------|---------------|----------|-------|-------|
| POST | `/api/chat` | PRODUCCION* | Condicional** | Scripts | *Fallback hybrid; **si `USE_HYBRID_CHAT=false` |
| POST | `/api/chat/hybrid` | PRODUCCION | Sí (default) | Sí (extenso) | Flujo principal |

### Semantic / Query pipeline

| Método | Path | Clasificación | Frontend | Tests |
|--------|------|---------------|----------|-------|
| GET | `/api/semantic/operation` | EXPERIMENTAL | No | Sí |
| GET | `/api/semantic/entity` | EXPERIMENTAL | No | Sí |
| GET | `/api/semantic/intent` | EXPERIMENTAL | No | Sí |
| GET | `/api/query/plan` | EXPERIMENTAL | No | Sí |
| GET | `/api/query/execute` | EXPERIMENTAL | No | Sí |
| GET | `/api/query/respond` | EXPERIMENTAL | No | Sí |

### Observabilidad — metrics

| Método | Path | Clasificación | Frontend | Tests |
|--------|------|---------------|----------|-------|
| GET | `/api/metrics/summary` | PRODUCCION | Sí (`metricsApi`) | Sí |
| GET | `/api/metrics/top-queries` | PRODUCCION | Sí | Sí |
| GET | `/api/metrics/performance` | PRODUCCION | Sí | Sí |
| GET | `/api/metrics/routing` | NO UTILIZADO | No | Sí |

### Business analytics (observabilidad híbrida)

| Método | Path | Clasificación | Frontend | Tests |
|--------|------|---------------|----------|-------|
| GET | `/api/analytics/coverage` | PRODUCCION | Sí | Sí |
| GET | `/api/analytics/performance` | PRODUCCION | Sí | Sí |
| GET | `/api/analytics/financial` | PRODUCCION | Sí | Sí |
| GET | `/api/analytics/top-queries` | PRODUCCION | Sí | Sí |
| GET | `/api/analytics/report` | PRODUCCION*** | Fetch sí, UI no | Sí |

***Datos obtenidos por `useBusinessAnalytics` pero no renderizados en `AnalyticsPage`.

### Operational audit

| Método | Path | Clasificación | Frontend | Tests |
|--------|------|---------------|----------|-------|
| GET | `/api/audit/overview` | PRODUCCION | Sí | Sí |
| GET | `/api/audit/coverage-gaps` | PRODUCCION | Sí | Sí |
| GET | `/api/audit/coverage-gaps/export` | PRODUCCION | Sí | Sí |
| GET | `/api/audit/top-routes` | PRODUCCION | Sí | Sí |
| GET | `/api/audit/top-failures` | PRODUCCION | Sí | Sí |
| GET | `/api/audit/adoption` | PRODUCCION | Sí | Sí |
| GET | `/api/audit/report` | NO UTILIZADO | No | Sí (1 integración) |

### Datamart analytics legacy

| Método | Path | Clasificación | Frontend | Tests | Scripts |
|--------|------|---------------|----------|-------|---------|
| GET | `/api/kpis` | NO UTILIZADO | No | No | `test_api.py` |
| GET | `/api/kpis/ejecutivos` | NO UTILIZADO | No | No | `test_api.py` |
| GET | `/api/top-clientes` | NO UTILIZADO | No | No | `test_api.py` |
| GET | `/api/top-proveedores` | NO UTILIZADO | No | No | `test_api.py` |
| GET | `/api/top-cuentas` | NO UTILIZADO | No | No | `test_api.py` |
| GET | `/api/resumen-mensual` | NO UTILIZADO | No | No | `test_api.py` |
| GET | `/api/evolucion-cliente/{codigo}` | NO UTILIZADO | No | No | `test_api.py` |
| GET | `/api/evolucion-proveedor/{codigo}` | NO UTILIZADO | No | No | `test_api.py` |
| GET | `/api/evolucion-cuenta/{codigo}` | NO UTILIZADO | No | No | `test_api.py` |

### Insights y metadata

| Método | Path | Clasificación | Frontend | Tests | Scripts |
|--------|------|---------------|----------|-------|---------|
| GET | `/api/insights` | NO UTILIZADO | No | No | `test_api.py` |
| GET | `/api/insights/resumen` | NO UTILIZADO | No | No | `test_api.py` |
| GET | `/api/metadata` | NO UTILIZADO | No | No | `test_metadata.py` |

---

## Resumen por clasificación

| Clasificación | Cantidad | % |
|---------------|----------|---|
| **PRODUCCION** | 18 | 46% |
| **EXPERIMENTAL** | 6 | 15% |
| **NO UTILIZADO** (sin UI) | 15 | 38% |

*Nota: `POST /api/chat` cuenta como PRODUCCION por rol de fallback activo.*

---

## Mapa frontend → API

| Servicio frontend | Endpoints consumidos |
|-------------------|---------------------|
| `chatApi.ts` | `POST /api/chat`, `POST /api/chat/hybrid` |
| `metricsApi.ts` | `/api/metrics/summary`, `performance`, `top-queries` |
| `businessAnalyticsApi.ts` | 5× `/api/analytics/*` |
| `operationalAuditApi.ts` | 6× `/api/audit/*` (incl. export) |
| `performanceApi.ts` | Reutiliza `chatApi` (benchmark local) |

**Endpoints backend sin cliente React:** 21 de 39.

---

## Duplicidad funcional detectada

| Dominio | Endpoints duplicados | Observación |
|---------|---------------------|-------------|
| Top queries | `/api/metrics/top-queries` vs `/api/analytics/top-queries` | Misma telemetría, distintos DTOs |
| Performance | `/api/metrics/performance` vs `/api/analytics/performance` | Agregación similar |
| KPIs datamart vs coverage | `/api/kpis` vs `/api/analytics/coverage` | Fuentes de datos distintas |

---

## Recomendación documental (no aplicada)

Priorizar en futura limpieza los 15 endpoints **NO UTILIZADO** por UI, comenzando por validar si algún consumidor externo (BI, scripts programados) depende de `/api/kpis*` o `/api/insights*`.
