# Technical Debt Assessment — Resumen Ejecutivo

**Proyecto:** Asistente de Inteligencia Empresarial Olnatura  
**Fecha:** 2026-06-23  
**Tipo:** Auditoría de deuda técnica (solo análisis — sin cambios en código)

---

## Objetivo cumplido

Se generó evidencia objetiva en 9 documentos de auditoría más este resumen ejecutivo, sin eliminar archivos, modificar comportamiento, tests ni base de datos.

| Documento | Contenido |
|-----------|-----------|
| `dependency_audit.md` | Dependencias backend/frontend |
| `dead_code_audit.md` | Código y componentes sin uso |
| `flow_audit.md` | Mapa de flujos ACTIVO/LEGACY/OBSOLETO |
| `endpoint_audit.md` | 39 endpoints clasificados |
| `frontend_audit.md` | Pages, components, hooks, services |
| `database_audit.md` | Tablas, MVs, índices, ORM |
| `observability_audit.md` | Métricas y duplicaciones |
| `test_audit.md` | Cobertura y huecos |
| `cleanup_candidates.md` | Tabla de candidatos con riesgo |

---

## Hallazgos principales

### 1. Arquitectura dual de chat (deuda crítica)

El sistema opera con **dos stacks paralelos**:

- **Activo:** `HybridChatRouter` → pipeline semántico → `BusinessQueryExecutor` + `response_engine`
- **Legacy:** `IntentRouter` (~608 líneas) → `services/deterministic_response_engine` → `ResponseGenerator`/Ollama

El hybrid **delega activamente** al legacy como último recurso (`handled_by=legacy_chat`). Eliminar legacy sin migración rompería cobertura de consultas abiertas.

### 2. Superficie API fragmentada

- **39 endpoints** registrados; solo **~17** consumidos por el frontend React.
- **15 endpoints** sin UI (datamart `/api/kpis*`, insights, metadata).
- **Duplicidad:** metrics vs business-analytics para top-queries y performance.

### 3. Duplicación de componentes homónimos

- Dos clases `DeterministicResponseEngine` con contratos distintos.
- Dos sistemas de intent (regex vs semántico).
- Coexistencia v1/v2 en `guided_fallback` y `capability_discovery`.

### 4. Observabilidad híbrida

- Métricas **duraderas** en PostgreSQL (`performance_metrics`) — bien integradas.
- Métricas **volátiles** in-memory (4 servicios) — se pierden al reiniciar; no aptas multi-worker sin cambio.

### 5. Frontend limpio con deuda menor

- 4 páginas activas, arquitectura consistente.
- **3 componentes** de performance sin usar.
- Fetch de `CoverageReport` sin renderizar.

### 6. Tests sólidos en pipeline nuevo; débiles en legacy

- **337 tests** backend; **335 pasan**, 2 fallos en query planner.
- Cobertura global **77%**; legacy chat/LLM **24–33%**.
- **24 scripts** manuales no integrados en CI.

### 7. Dependencias mal segmentadas

- `pandas`, `openpyxl`, `pytest` en `requirements.txt` de producción sin uso en `app/`.

---

## Riesgos

| Riesgo | Severidad | Mitigación recomendada |
|--------|-----------|------------------------|
| Retirar legacy chat sin plan | **Crítica** | Medir % `legacy_chat` en audit antes de eliminar |
| Multi-worker con memoria in-process | **Alta** | Externalizar conversation memory o sticky sessions |
| MVs desactualizadas | **Media** | Documentar/automatizar REFRESH |
| Tests fallidos query planner | **Media** | Corregir antes de refactor |
| Endpoints kpis usados externamente | **Media** | Inventariar consumidores fuera de React |
| Crecimiento `performance_metrics` | **Baja** | Política de retención |

---

## Complejidad actual

| Dimensión | Evaluación |
|-----------|------------|
| Módulos Python en `app/` | ~153 archivos, ~11.500 líneas |
| Routers FastAPI | 13 |
| Módulos conversacionales | 6 paquetes (+ 2 sub-v2) |
| Capas legacy NLP/LLM | ~15 módulos interdependientes |
| Páginas React | 4 |
| Migraciones DB | 7 |
| Documentación funcional (`docs/`) | 15+ archivos v1/v2 |

**Complejidad global:** **Alta** — resultado esperado de múltiples sprints incrementales sin fase de consolidación.

---

## Estimación de código por naturaleza

| Naturaleza | Backend (líneas est.) | Frontend | Notas |
|------------|----------------------|----------|-------|
| **Activo** | ~5.500–6.500 (48–57%) | 30 componentes, 6 hooks | Hybrid + dashboards |
| **Legacy activo** | ~3.500–4.000 (30–35%) | 1 path chat condicional | IntentRouter stack |
| **Compartido/infra** | ~1.500–2.000 (13–17%) | i18n, layout | Models, deps, schemas |
| **Obsoleto/huérfano** | ~300 (3%) | 3 componentes | Sin path UI |

---

## Entregable final — métricas clave

| Métrica | Valor |
|---------|-------|
| **Endpoints activos (producción UI + hybrid)** | **18** |
| **Endpoints legacy (datamart/insights sin UI)** | **12** |
| **Endpoints experimentales (semantic/query)** | **6** |
| **Endpoints no utilizados por frontend** | **21** de 39 |
| **Componentes frontend activos** | **30** |
| **Componentes candidatos a eliminación** | **3** |
| **Módulos backend candidatos a consolidación** | **~8–10** (chat legacy, analytics legacy, motores duplicados) |
| **Candidatos totales documentados** | **27** |
| **Cobertura tests backend** | **77%** |
| **Tests backend** | **337** (2 fallidos) |
| **Dependencias prod sin uso en app/** | **3** |

---

## Principales fuentes de deuda técnica (ordenadas)

1. **Dualidad arquitectónica chat** (IntentRouter vs Semantic Pipeline)
2. **API surface sin consumidor** (kpis, insights, metadata)
3. **Homónimos y duplicación** (DeterministicResponseEngine, analytics endpoints)
4. **Coexistencia v1/v2** sin deprecación formal
5. **Métricas in-memory no duraderas**
6. **Cobertura de tests insuficiente en legacy**
7. **Scripts manuales vs automatización**
8. **Dependencias y assets huérfanos** (menor impacto)

---

## Recomendación final

| Opción | Cuándo aplicar |
|--------|----------------|
| **1. Mantener** | Corto plazo pre-pruebas operacionales — sistema funciona; deuda es conocida y acotada |
| **2. Consolidar** | **Recomendado como siguiente fase** — unificar endpoints duplicados, integrar UI faltante, persistir métricas v2, segmentar dependencias, eliminar componentes huérfanos |
| **3. Eliminar** | Solo tras medición de tráfico `legacy_chat` < umbral acordado, tests de regresión ≥80% en módulos afectados, y confirmación de no consumidores externos de APIs datamart |

### Plan sugerido en tres olas

```
Ola 1 (bajo riesgo):  cleanup frontend huérfano + requirements + assets
Ola 2 (medio riesgo): consolidar APIs analytics/metrics + integrar report en UI
Ola 3 (alto riesgo):  migrar legacy_chat → ampliar pipeline + retirar IntentRouter
```

---

## Conclusión

Olnatura IA_MVP es un sistema **funcionalmente maduro** con deuda técnica **típica de evolución incremental**: la capa de producción (hybrid + observabilidad + React) está razonablemente cohesionada, pero arrastra un **stack legacy completo** que sigue siendo **red de seguridad activa**, no código muerto.

La limpieza controlada debe basarse en:

1. Telemetría de `handled_by` desde Operational Audit
2. Corrección de 2 tests fallidos
3. Inventario de consumidores externos de `/api/kpis*`
4. Ejecución por olas según `cleanup_candidates.md`

**Ningún cambio fue aplicado en esta auditoría** — el repositorio permanece intacto para pruebas operacionales.
