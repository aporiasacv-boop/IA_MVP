# Dead Code Audit — Asistente de Inteligencia Empresarial Olnatura

**Fecha:** 2026-06-23  
**Modo:** Análisis estático — sin eliminar ni modificar código.

---

## Metodología

- Búsqueda de definiciones vs referencias (`grep`, cadenas de importación).
- Cruce endpoints registrados vs consumidores (frontend, tests, scripts).
- Clasificación: **Muerto confirmado**, **Muerto en runtime** (solo scripts), **Activo indirecto**, **Falso positivo**.

---

## Backend — clases y servicios

| Elemento | Tipo | Estado | Evidencia |
|----------|------|--------|-----------|
| `ExecutiveSummaryService` | Clase | **Muerto en runtime** | Solo importado en `scripts/build_executive_summaries.py`; 0 referencias en `app/api`, `app/services` (excepto definición) |
| `DeterministicResponseEngine` (`services/`) | Clase | **Activo (legacy)** | Usado por `app/api/routes/chat.py` |
| `DeterministicResponseEngine` (`response_engine/`) | Clase | **Activo (pipeline)** | Usado por hybrid router y `/api/query/respond` |
| `IntentRouter` | Clase | **Activo (legacy)** | Instancia global en `chat.py` L57 |
| `HybridChatRouter` | Clase | **Activo (principal)** | `hybrid_chat.py`, `deps.py` |
| `GuidedFallbackEngine` v1 | Clase | **Activo** | Invocado desde `guided_fallback/engine.py` (v2 es extensión, no reemplazo total) |
| `CapabilityDiscoveryEngine` v1 | Clase | **Activo** | Delega a v2 en `engine.py` |
| `ConversationMemoryService` | Clase | **Activo** | Hybrid router |
| `SlotClarificationEngine` | Clase | **Activo** | Hybrid router |
| `SuggestedQuestionsEngine` | Clase | **Activo** | Hybrid router post-respuesta |
| `CoverageRecoveryMetricsService` | Clase | **Activo** | Hybrid router + metrics summary |
| `AnalyticsService` | Clase | **Activo** | `/api/kpis*` (sin frontend) |
| `InsightsEngine` | Clase | **Activo** | `/api/insights*` (sin frontend) |
| `MetadataService` | Clase | **Activo** | `/api/metadata` (solo scripts) |
| `UploadService` | Clase | **Activo** | `/upload` (sin frontend) |

### Capas legacy usadas solo por `POST /api/chat`

| Módulo | Líneas aprox. | Consumidor |
|--------|---------------|------------|
| `intent_router.py` | 608 | `chat.py` |
| `deterministic_response_engine.py` (services) | 413 | `chat.py` |
| `response_generator.py` | 334 | `chat.py` |
| `query_executor.py` (services) | 121 | `chat.py` |
| `executive_capability_layer.py` | 269 | `chat.py` |
| `token_optimization_layer.py` | 51 | `chat.py` |
| `social_identity_layer.py` | 250 | `chat.py` |
| `system_explanation_layer.py` | 152 | `chat.py` |
| `human_language_layer.py` | ~80 | `chat.py` |
| `entity_extraction_layer.py` | 66 | `chat.py` |
| `business_context_builder.py` | 236 | `response_generator.py` |
| `llm_context_optimizer.py` | 121 | `response_generator.py` |
| `prompt_builder.py` | 25 | `response_generator.py` |
| `prompt_audit.py` | 15 | `response_generator.py` |
| `temporal_resolver.py` | 81 | `response_generator.py`, `business_context_builder.py` |

**Nota:** No son "muertos" mientras hybrid delegue a legacy y el frontend pueda usar `POST /api/chat`.

---

## Backend — endpoints registrados sin consumo en producción UI

| Router / endpoint | Registrado | Frontend | Tests pytest | Scripts |
|-------------------|------------|----------|--------------|---------|
| `GET /api/kpis*` (9 rutas) | Sí | No | No | `scripts/test_api.py` |
| `GET /api/insights*` | Sí | No | No | `scripts/test_api.py` |
| `GET /api/metadata` | Sí | No | No | `scripts/test_metadata.py` |
| `POST /upload` | Sí | No | No | — |
| `GET /api/semantic/*` | Sí | No | Sí | — |
| `GET /api/query/*` | Sí | No | Sí | — |
| `GET /api/metrics/routing` | Sí | No | Sí | — |
| `GET /api/audit/report` | Sí | No | Sí (1 test) | — |

---

## Backend — schemas / DTOs con baja referencia

| Schema | Archivo | Referencia |
|--------|---------|------------|
| `RoutingMetricsResponse` | `app/schemas/metrics.py` | API `/api/metrics/routing`; sin frontend |
| `DomainFallbackMetricsResponse` | `operational_audit/schemas.py` | Embebido en `/api/audit/report`; endpoint sin UI |
| Schemas analytics legacy | `app/schemas/analytics.py` | Solo rutas `/api/kpis*` |

---

## Frontend — componentes no renderizados

| Componente | Archivo | Estado |
|------------|---------|--------|
| `PerformanceMetricsGrid` | `components/performance/PerformanceMetricsGrid.tsx` | **Muerto** — 0 imports |
| `CostOptimizationSection` | `components/performance/CostOptimizationSection.tsx` | **Muerto** — 0 imports |
| `PerformanceHero` | `components/performance/PerformanceHero.tsx` | **Muerto** — 0 imports |

Funcionalidad equivalente parcial en `ExecutiveSummarySection` y `SmartSavingsHero` dentro de `PerformancePage`.

---

## Frontend — tipos huérfanos

| Tipo | Archivo | Estado |
|------|---------|--------|
| `RoutingMetrics` | `types/metrics.ts` | **Huérfano** — 0 imports |
| `HandledByDistributionItem` | `types/metrics.ts` | **Huérfano** |
| `RoutingPathItem` | `types/metrics.ts` | **Huérfano** |
| `CostOptimizationExample` | `types/performance.ts` | **Huérfano** — solo usado por componente muerto |
| `CoverageReport` | `types/businessAnalytics.ts` | **Fetch sin UI** — `useBusinessAnalytics` lo obtiene pero `AnalyticsPage` no lo muestra |

---

## Frontend — exports y constantes legacy

| Elemento | Archivo | Estado |
|----------|---------|--------|
| `QUICK_SUGGESTIONS` | `constants/suggestions.ts` | Marcado `@deprecated`; 0 consumidores |
| `translateDomain` | `i18n/spanish.ts` | Solo tests; no UI productiva |
| `sendLegacyChatQuestion` | `services/chatApi.ts` | Export interno; uso condicional vía flag |
| `runPerformanceBenchmark` | `services/performanceApi.ts` | Export sin import externo |

---

## Frontend — hooks y páginas

| Categoría | Total | Huérfanos |
|-----------|-------|-----------|
| Páginas | 4 enrutadas + 1 test | 0 |
| Hooks | 6 | 0 |
| Servicios | 6 archivos | 0 archivos huérfanos |

---

## Scripts de prueba manual (`scripts/test_*.py`)

24 scripts orientados al stack legacy (`IntentRouter`, `/api/chat`, capas NLP). No son código muerto del runtime pero representan **deuda de automatización** (no integrados en pytest CI estándar).

---

## Resumen cuantitativo

| Categoría | Cantidad estimada |
|-----------|-------------------|
| Módulos backend muertos en runtime | 1 (`ExecutiveSummaryService` en app; usado solo en script ETL) |
| Componentes React muertos | 3 |
| Tipos TypeScript huérfanos | 4–5 |
| Endpoints sin consumidor frontend | ~18 de 39 |
| Capas legacy activas solo vía chat | ~15 módulos (~2.800+ líneas) |
