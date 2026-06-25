# Test Audit — Asistente de Inteligencia Empresarial Olnatura

**Fecha:** 2026-06-23  
**Ejecución:** `pytest tests/` con `--cov=app` (solo lectura de resultados; tests no modificados).

---

## Resumen de ejecución

| Métrica | Valor |
|---------|-------|
| Tests recolectados | 337 |
| Tests pasados (última ejecución) | 335 |
| Tests fallidos | 2 |
| Cobertura global `app/` | **77%** (4.968 stmts, 1.129 miss) |
| Archivos con cobertura 100% | 103 (skip-covered en reporte) |

### Tests fallidos (estado existente — no corregidos en esta auditoría)

| Test | Archivo | Área |
|------|---------|------|
| `test_plan_system_capability_questions_from_question[¿Qué datos tienes?]` | `tests/test_query_planner.py` | Query planner |
| `test_query_plan_endpoint_system_capability_questions[¿Qué datos tienes?]` | `tests/test_query_planner.py` | Endpoint `/api/query/plan` |

---

## Backend — inventario de tests

### Unitarios (`tests/*.py`) — 28 archivos

| Archivo | Módulo cubierto | Cobertura relativa |
|---------|-----------------|-------------------|
| `test_api.py` | health, version | Básica |
| `test_hybrid_chat_router.py` | HybridChatRouter | Alta |
| `test_semantic_intent_builder.py` | Semantic + endpoint | Alta |
| `test_entity_resolver.py` | Entity resolver + endpoint | Alta |
| `test_operation_resolver.py` | Operation resolver + endpoint | Alta |
| `test_query_planner.py` | Planner + endpoint | Alta (2 fallos) |
| `test_business_query_executor.py` | Executor (mocked) | Alta |
| `test_deterministic_response_engine.py` | Response engine **nuevo** | Alta |
| `test_slot_clarification_engine.py` | Slot clarification | Alta |
| `test_conversation_memory.py` | Memory + hybrid | Alta |
| `test_guided_fallback_engine.py` | Fallback v1 | Alta |
| `test_guided_fallback_v2.py` | Fallback v2 | ~97% módulo v2 |
| `test_capability_discovery_engine.py` | Discovery + v2 | Alta |
| `test_capability_discovery_health.py` | Health | Alta |
| `test_coverage_recovery.py` | Coverage recovery | Alta |
| `test_system_capabilities_queries.py` | Hybrid capabilities | Media |
| `test_suggested_questions_engine.py` | Sugerencias | ~89% |
| `test_suggested_questions_health.py` | Health | Alta |
| `test_observability.py` | Metrics stack + endpoints | Alta |
| `test_business_analytics_service.py` | Business analytics | Alta |
| `test_business_analytics_health.py` | Health | Alta |
| `test_operational_audit_service.py` | Audit service | Alta |
| `test_operational_audit_health.py` | Health | Alta |

### Integración (`tests/integration/`) — 9 archivos

| Archivo | Alcance |
|---------|---------|
| `test_hybrid_chat_integration.py` | E2E hybrid (memory, fallback, legacy) |
| `test_guided_fallback_v2_integration.py` | Fallback v2 + metrics/audit |
| `test_capability_discovery_v2_integration.py` | Discovery v2 E2E |
| `test_coverage_recovery_integration.py` | Recovery + métricas |
| `test_observability_integration.py` | Persistencia post-hybrid |
| `test_operational_audit_integration.py` | Todos `/api/audit/*` |
| `test_business_analytics_integration.py` | Todos `/api/analytics/*` |
| `test_query_executor_integration.py` | Executor vs datamart |
| `test_response_engine_integration.py` | Pipeline + `/api/query/respond` |

---

## Frontend — inventario de tests

| Archivo | Alcance | Tests |
|---------|---------|-------|
| `i18n/spanish.test.ts` | Catálogo i18n | 15+ |
| `i18n/spanishLocalization.integration.test.tsx` | Analytics + Audit UI | 3 |
| `pages/OperationalAuditPage.test.tsx` | Audit page | 3 |
| `services/chatApi.test.ts` | Mapeo hybrid/legacy | 3 |
| `services/performanceStore.test.ts` | Store local | 2 |
| `types/businessAnalytics.test.ts` | Tipos | 2 |
| `types/metrics.test.ts` | Tipos | 3 |
| `config/featureFlags.test.ts` | Flags | 5 |

**Total frontend:** ~35 tests (vitest).

---

## Módulos backend sin tests dedicados (huecos)

| Módulo / área | Cobertura medida | Riesgo |
|---------------|------------------|--------|
| `app/api/routes/chat.py` (legacy completo) | Baja / indirecta | **Alto** |
| `app/services/intent_router.py` | ~68% | **Alto** |
| `app/services/response_generator.py` | ~24% | **Alto** |
| `app/services/deterministic_response_engine.py` (legacy) | ~33% | Medio |
| `app/services/executive_summary_service.py` | 0% | Bajo (solo ETL) |
| `app/api/routes/analytics.py` (kpis) | 0% | Medio |
| `app/api/routes/insights.py` | 0% | Medio |
| `app/api/routes/metadata.py` | 0% | Bajo |
| `app/api/routes/upload.py` | 0% | Bajo |
| `app/services/ollama_client.py` | ~31% | Medio |

---

## Scripts manuales vs pytest

| Tipo | Cantidad | Integración CI |
|------|----------|----------------|
| `scripts/test_*.py` | ~15 | **No** (manual) |
| `frontend/scripts/test_chat_api.mjs` | 1 | **No** |
| `tests/` pytest | 37 archivos | **Sí** |

**Deuda:** 24 scripts de prueba manual duplican escenarios que deberían vivir en pytest (especialmente legacy chat e IntentRouter).

---

## Tests huérfanos / redundantes

| Observación | Detalle |
|-------------|---------|
| Redundancia metrics vs analytics | Tests de integración cubren ambas familias por separado — válido pero duplicado en setup |
| Health tests | Múltiples `*_health.py` con patrones similares — posible consolidación futura |
| `types/*.test.ts` | Validación estructural mínima — bajo valor vs integración |

No se identificaron archivos de test **completamente huérfanos** (sin asserts ni imports válidos).

---

## Cobertura por capa (estimación de pytest --cov)

| Capa | Cobertura típica |
|------|------------------|
| Hybrid router + módulos conversacionales | 85–97% |
| Query engine / executor / response engine nuevo | 90%+ |
| Observability + audit + business analytics | 85%+ |
| Legacy chat stack | 25–50% |
| Datamart services (analytics, insights) | 26–53% |

---

## Recomendaciones documentales

1. Corregir 2 tests fallidos de query planner antes de limpieza legacy.
2. Añadir tests de regresión para `POST /api/chat` o documentar su retirada planificada.
3. Migrar scripts `test_chat.py`, `test_router.py` a pytest.
4. Objetivo de cobertura pre-limpieza: **≥80% en módulos marcados para eliminación** (para detectar regresiones).

---

## Resumen

| Métrica | Valor |
|---------|-------|
| Tests backend | 337 |
| Tests frontend | ~35 |
| Módulos `app/` sin tests | ~10 áreas |
| Scripts manuales no automatizados | 24 |
| Cobertura global backend | 77% |
