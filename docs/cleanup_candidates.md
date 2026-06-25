# Cleanup Candidates — Asistente de Inteligencia Empresarial Olnatura

**Fecha:** 2026-06-23  
**Actualización RC1:** Elementos marcados como ✅ fueron eliminados en la consolidación RC1.

---

## Ejecutado en RC1 ✅

| Elemento | Acción |
|----------|--------|
| `AICostsPage.tsx`, `useAICosts`, `aiCostsApi` | Eliminados |
| `useBusinessKnowledge`, `businessKnowledgeApi` | Eliminados |
| `PerformanceHero`, `PerformanceMetricsGrid`, `CostOptimizationSection` | Eliminados |
| `AICostPanels` | Eliminado |
| `QUICK_SUGGESTIONS` | Eliminado |
| `RoutingMetrics` (tipos TS) | Eliminado |

**Total eliminado:** 11 artefactos frontend sin consumidores.

---

## Tabla de candidatos pendientes

| Elemento | Tipo | Razón | Impacto | Riesgo |
|----------|------|-------|---------|--------|
| `app/services/intent_router.py` | Router / servicio | Reemplazado funcionalmente por `SemanticIntentBuilder` + planners; aún usado como fallback legacy | Alto (608 líneas) | **Alto** — último recurso hybrid |
| `app/api/routes/chat.py` | Endpoint | Duplica superficie de `hybrid_chat`; delegado interno activo | Alto | **Alto** |
| `app/services/deterministic_response_engine.py` | Motor respuesta | Duplicado homónimo en `response_engine/`; solo legacy chat | Medio | **Medio** |
| `app/services/response_generator.py` | Servicio LLM | Solo legacy; Ollama en conversación general | Medio | **Medio** |
| `app/services/query_executor.py` | Ejecutor | Legacy por `Intent`; pipeline usa `business_query_executor` | Medio | Medio |
| `app/api/routes/analytics.py` | Router (9 endpoints) | Sin consumidor frontend; solapa con `/api/analytics/*` | Medio | Bajo* |
| `app/api/routes/insights.py` | Router | Sin UI; solo scripts | Bajo | Bajo |
| `app/api/routes/metadata.py` | Router | Sin UI; solo scripts | Bajo | Bajo |
| `app/repositories/analytics_repository.py` | Repositorio | Solo APIs legacy kpis | Medio | Bajo |
| `app/services/analytics_service.py` | Servicio | Solo APIs legacy | Medio | Bajo |
| `app/services/insights_engine.py` | Servicio | Sin UI | Bajo | Bajo |
| `GET /api/metrics/routing` | Endpoint | Sin frontend; datos en summary parcial | Bajo | Bajo |
| `GET /api/audit/report` | Endpoint | Sin UI; dominio fallback | Bajo | Bajo |
| `frontend/.../PerformanceMetricsGrid.tsx` | Componente React | 0 imports; sustituido | Bajo | ✅ RC1 |
| `frontend/.../CostOptimizationSection.tsx` | Componente React | 0 imports | Bajo | ✅ RC1 |
| `frontend/.../PerformanceHero.tsx` | Componente React | 0 imports | Bajo | ✅ RC1 |
| `frontend/types/metrics.ts` → `RoutingMetrics` | Tipo TS | Sin servicio ni UI | Bajo | **Bajo** |
| `frontend/constants/suggestions.ts` → `QUICK_SUGGESTIONS` | Constante | Deprecada | Bajo | **Bajo** |
| `pandas` + `openpyxl` en `requirements.txt` | Dependencia | Solo scripts ETL | Bajo | **Bajo** |
| `pytest` en `requirements.txt` | Dependencia | Debería ser dev-only | Bajo | **Bajo** |
| `scripts/test_*.py` (24 archivos) | Scripts | Duplican pytest manual | Medio | Bajo |
| `app/services/executive_summary_service.py` | Servicio ETL | Solo `build_executive_summaries.py`; no runtime | Bajo | Bajo |
| `guided_fallback/` lógica v1 | Submódulo | v2 activo; v1 aún en path | Medio | **Medio** |
| `capability_discovery/` formatter v1 | Submódulo | v2 es principal en engine | Bajo | Medio |
| Métricas in-memory (4 servicios) | Observabilidad | Volátiles; duplican parcialmente DB | Medio | Medio |
| `src/assets/vite.svg`, `public/icons.svg` | Assets | Sin referencia | Bajo | **Bajo** |

\*Riesgo bajo solo si no hay consumidores externos (BI, integraciones) de `/api/kpis*`.

---

## Candidatos a consolidación (no eliminación inmediata)

| Elemento A | Elemento B | Acción sugerida | Impacto | Riesgo |
|------------|------------|-----------------|--------|--------|
| `/api/metrics/top-queries` | `/api/analytics/top-queries` | Unificar DTO y endpoint | Medio | Medio |
| `/api/metrics/performance` | `/api/analytics/performance` | Idem | Medio | Medio |
| `DeterministicResponseEngine` (×2) | — | Renombrar y unificar contrato | Alto | Alto |
| `IntentRouter` | `SemanticIntentBuilder` | Migrar patrones legacy a catálogo | Alto | Alto |
| `POST /api/chat` | `POST /api/chat/hybrid` | Unificar en un solo endpoint | Alto | Alto |
| `CoverageReport` fetch | `AnalyticsPage` UI | Mostrar o dejar de fetchear | Bajo | **Bajo** |
| `performance_metrics` + in-memory | — | Persistir métricas v2 en DB | Medio | Medio |

---

## Priorización sugerida para fase de limpieza

### Fase A — Riesgo bajo (candidatos a eliminación temprana)

1. Componentes React huérfanos (3)
2. Tipos y constantes deprecadas frontend
3. Assets sin referencia
4. Segmentar `requirements.txt` (dev vs prod)
5. `QUICK_SUGGESTIONS` deprecado

### Fase B — Riesgo medio (requiere validación de consumidores)

1. Endpoints `/api/kpis*`, `/api/insights*`, `/api/metadata`
2. `GET /api/metrics/routing` o integrarlo en frontend
3. `GET /api/audit/report` o integrarlo en Operational Audit UI
4. Migrar scripts manuales a pytest

### Fase C — Riesgo alto (requiere plan de migración y pruebas operacionales)

1. Retirada progresiva de `IntentRouter` y capas NLP legacy
2. Consolidación de endpoints chat
3. Unificación de motores de respuesta determinista
4. Persistencia de métricas in-memory
5. Retiro de fallback `legacy_chat` en hybrid

---

## Elementos que NO deben eliminarse sin análisis adicional

| Elemento | Razón |
|----------|-------|
| `HybridChatRouter` | Núcleo de producción |
| `performance_metrics` | Fuente única de dashboards |
| Tablas `*_resumen` y MVs | Datos del pipeline |
| `conversation_memory`, `slot_clarification` | Funcionalidad activa |
| `ollama_client.py` | Aún requerido para legacy_chat |
| Tests de integración hybrid | Red de seguridad pre-limpieza |

---

## Conteo de candidatos

| Severidad | Cantidad |
|-----------|----------|
| Eliminación directa (riesgo bajo) | ~12 |
| Consolidación | ~7 |
| Migración mayor (riesgo alto) | ~5 |
| **Total elementos listados** | **27** |
