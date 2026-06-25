# Informe de preparación para producción — Olnatura Intelligence

**Fecha:** 23 de junio de 2026  
**Alcance:** Auditoría de solo lectura (sin modificación de código)  
**Objetivo:** Determinar si la plataforma está lista para piloto con usuarios reales y demostraciones ejecutivas con Dirección.

---

## Estado general: **68 / 100**

| Dimensión | Puntuación | Lectura ejecutiva |
|-----------|:----------:|-------------------|
| Arquitectura | 62 | Funcional pero con duplicidades estructurales importantes |
| Backend | 78 | Pipeline híbrido operativo; 690 tests; cobertura 85% |
| Frontend | 82 | 13 pantallas conectadas; localización mayormente completa |
| Observabilidad | 65 | Métricas ricas en backend; UI muestra subconjunto; duplicación |
| Business Knowledge | 58 | Contenido abundante; **no integrado al chat** |
| Inteligencia empresarial (IA) | 68 | Executive Response condicionado; EKO/ERO solo en rama ejecutiva |
| Costos | 74 | Panel de costos IA operativo; proveedor mock por defecto |
| Seguridad | 35 | **Bloqueante para piloto externo** — sin autenticación |
| Experiencia de usuario | 72 | Pulido reciente; inconsistencias en capacidades y sugerencias |

**Veredicto sintético:** Apto para **demo controlada** con guion y datos preparados. **No apto** para piloto abierto con usuarios reales sin endurecimiento de seguridad y alineación conocimiento ↔ runtime.

---

## 1. Arquitectura

### 1.1 Hallazgos verificados

#### Duplicidades estructurales (deuda principal)

| Área | Instancias | Evidencia |
|------|------------|-----------|
| Motor determinístico | `app/services/deterministic_response_engine.py` (legacy) vs `app/response_engine/deterministic_response_engine.py` (business pipeline) | Alias `BusinessQueryResponseEngine` en `deps.py` |
| Chat | `POST /api/chat` (legacy multi-capa) vs `POST /api/chat/hybrid` (router nuevo) | Frontend usa hybrid por defecto (`VITE_USE_HYBRID_CHAT`) |
| Intención semántica | `SemanticIntentBuilder` (planner SQL) vs `app/semantic_intent/` SBEP (EEP/EKO/ERO) | Solo SBEP en `evidence_package` y executive reasoning |
| Conocimiento | `enterprise_knowledge` (PostgreSQL) vs `knowledge_pack/` (Markdown) | Sin integración entre ambos ni con chat |
| Identidad | `social_identity_layer.py` (legacy) vs `product_identity/` (hybrid) | Misma marca, dos interceptores |
| Cliente LLM | `ollama_client.py` vs `ai_orchestration/providers/ollama_provider.py` | Stacks separados |
| Analytics | `app/api/routes/analytics.py` (datamart KPIs) vs `business_analytics.py` (métricas de producto) | Prefijos distintos; naming confuso |

#### Candidatos a código muerto u obsoleto (no eliminar sin validación)

| Candidato | Justificación | Riesgo si se elimina |
|-----------|---------------|----------------------|
| Pipeline legacy completo (`chat.py` + capas HLL, token optimization, etc.) | Solo usado como `legacy_delegate` y fallback `VITE_USE_HYBRID_CHAT=false` | Romper definiciones delegadas a legacy |
| `ExecutiveSummaryService` | Solo `scripts/build_executive_summaries.py` | Scripts ETL, no runtime |
| `get_conversation_memory_service()` en `deps.py` | Factory sin consumidor `Depends` | Bajo — limpieza cosmética |
| Endpoints datamart (`/api/kpis`, `/top-*`, `/insights`) | Solo scripts de prueba | Posible uso ops/BI externo |
| `/api/semantic/*`, `/api/query/*` | Herramientas debug; sin frontend | Útiles para diagnóstico |
| `knowledge_pack` API completa | Sin UI; sin chat | Sprint futuro de integración |
| `PerformanceHero`, `PerformanceMetricsGrid`, `CostOptimizationSection` | Componentes React sin import | Código muerto frontend |
| `generateExecutiveResponse`, `getExecutiveStatistics` en `aiCostsApi.ts` | Exportados, no usados en páginas | Deuda frontend |
| `pandas` / `openpyxl` en `requirements.txt` | Solo scripts ETL | Mover a requirements-dev |

#### Servicios sin consumidor en runtime conversacional

- `BusinessKnowledgePackService` — API REST + tests únicamente.
- `ExecutiveSummaryService` — scripts únicamente.
- ~40 endpoints registrados sin consumidor activo en UI (upload, datamart legacy, knowledge-pack, executive-response parcial, metrics/routing, audit/report).

#### Migraciones Alembic

Cadena lineal 001→013, sin ramas huérfanas. **No se recomienda eliminar ninguna** en entornos desplegados. Solapamiento conceptual entre datamart v1/v2 y `cliente_resumen` es evolutivo, no erróneo.

### 1.2 Diagrama de arquitectura actual

```
Frontend (13 pantallas + chat)
    │
    ├─► POST /api/chat/hybrid ──► product_identity (pre-interceptor)
    │         │
    │         └─► HybridChatRouter
    │               ├─► conversation_memory
    │               ├─► capability_discovery (bypass post-planner)
    │               ├─► business_pipeline (10 query types)
    │               ├─► slot_clarification
    │               ├─► executive_reasoning (EEP→EKO/ERO→LLM)
    │               ├─► guided_fallback
    │               └─► legacy_chat (/api/chat interno)
    │
    └─► 12 dominios enterprise (entidades, ontología, evidencia, etc.)

knowledge_pack/ ──► API ──► (sin conexión al chat)
```

---

## 2. Pipeline — Flujo verificado

### 2.1 Secuencia real en `POST /api/chat/hybrid`

| Paso | ¿Invocado? | Notas |
|------|:----------:|-------|
| Product Identity | Sí (pre-router) | Intercepta identidad/capacidades antes del router |
| Hybrid Router | Sí | Orquestador central |
| Conversation Memory | Sí (primero) | Bypass total si hay hit; **no persiste entre reinicios** |
| SemanticIntentBuilder + BusinessQueryPlanner | Sí (rama business) | **No es SBEP** — parser paralelo |
| Capability Discovery | Sí | **Bypass post-planner** — anula `SYSTEM_CAPABILITIES` |
| Business Pipeline | Sí | 10 query types SQL deterministas |
| Slot Clarification | Sí | Solo 3 query types con slots obligatorios |
| Guided Fallback | Sí | Antes de legacy; delega definiciones a legacy |
| SBEP / Semantic Planner | Solo executive_reasoning | Invisible en path determinista |
| EKO | Solo executive_reasoning | Vía `EvidencePackageService.build()` |
| ERO | Solo executive_reasoning | Idem |
| EEP | Solo executive_reasoning | Idem |
| AI Orchestration | Solo executive_reasoning | Verbos: evaluar, diagnosticar, recomendar, etc. |
| Executive Response | Solo executive_reasoning | Requiere EKO/ERO en BD o activa guard de alucinación |
| Frontend | Sí | Hybrid por defecto; panel ejecutivo en respuestas |

### 2.2 Saltos innecesarios o inconsistentes

1. **Triple canal de “capacidades”:** `product_identity` («¿Qué puedes hacer?») vs `capability_discovery` («¿Qué puedo preguntarte?») vs `SYSTEM_CAPABILITIES` (planner, raramente ejecutado).
2. **Capability discovery después del planner:** trabajo de planificación desperdiciado.
3. **Definiciones empresariales → legacy LLM** en lugar de FAQ del knowledge pack («¿Qué es un proveedor?»).
4. **Executive stack condicionado:** consultas soportadas por SQL nunca usan EKO/ERO aunque la entidad tenga perfil ejecutivo.
5. **Dos planificadores semánticos** sin unificación — complejidad operativa.

---

## 3. Backend

### 3.1 Fortalezas

- **690 tests pasando** (unitarios + integración).
- **Cobertura global `app/`: 85%** (ejecución 23-jun-2026).
- Pipeline híbrido con tests de integración E2E (`test_hybrid_chat_integration.py`, coverage recovery, capability discovery v2).
- Módulos enterprise con patrón consistente (repository + service + health + metrics).
- Product identity integrado sin modificar Hybrid Router interno.

### 3.2 Debilidades

| Módulo / área | Cobertura aprox. | Riesgo |
|---------------|------------------|--------|
| `temporal_resolver.py` | 25% | Preguntas temporales ambiguas |
| `upload_service.py` | 45% | Upload sin auth |
| `chat.py` (legacy) | Baja | Fallback activo |
| `response_generator.py` | ~24% (histórico) | Legacy LLM |
| Conversation memory | In-process | Pérdida en restart / multi-worker |

### 3.3 Query types soportados (10)

`COUNT_CLIENTES`, `COUNT_PROVEEDORES`, `TOP_CLIENTES`, `TOP_PROVEEDORES`, `MAX_PROVEEDOR_MES`, `MAX_TRANSACCION_CLIENTE`, `LOOKUP_CLIENTE_BY_CUENTA`, `SYSTEM_CAPABILITIES`, `DATA_COVERAGE`, `DATASET_INFO`.

**No soportados (comunes en demo):** agregaciones SUM/AVG, tendencias, comparaciones, actividad temporal genérica («¿Qué pasó en junio?»), KPIs de liquidez/concentración prometidos en capability v2.

---

## 4. Frontend

### 4.1 Cobertura pantalla ↔ backend

| Sección | Ruta | API | Estado |
|---------|------|-----|--------|
| Asistente IA | `/` | `/api/chat/hybrid` | ✅ |
| Rendimiento | `/rendimiento` | `/api/metrics/*` + localStorage | ✅ Mixto |
| Analítica | `/analytics` | `/api/analytics/*` | ✅ (`/report` fetcheado, no renderizado) |
| Auditoría | `/audit` | `/api/audit/*` | ✅ |
| Costos IA | `/costos-ia` | `/api/ai-costs/summary` | ✅ Parcial |
| Entidades | `/entidades` | `/api/business-entities/*` | ✅ |
| Canónicas | `/canonicas` | `/api/canonical-entities/*` | ✅ |
| Perfiles | `/perfiles` | `/api/entity-profiles/*` | ✅ |
| Ontología | `/ontologia` | `/api/business-ontology` | ✅ (no usa `/types`, `/assignments`) |
| Conocimiento | `/conocimiento` | `/api/knowledge/*` | ✅ |
| Razonamiento | `/razonamiento` | `/api/reasoning/*` | ✅ |
| Intención Semántica | `/intencion-semántica` | `/api/semantic-intent/*` | ✅ |
| Evidencia | `/evidencia` | `/api/evidence/*` | ✅ |

### 4.2 Endpoints importantes sin pantalla

- `POST /upload`
- `/api/knowledge-pack/*` (6 rutas)
- Datamart legacy (`/api/kpis`, `/top-*`, `/insights`, `/resumen-mensual`)
- `/api/metrics/routing`
- `/api/executive-response/generate-from-package`, `/schema`, `/health`
- `/api/audit/report`

### 4.3 Componentes React huérfanos

- `PerformanceHero.tsx`
- `PerformanceMetricsGrid.tsx`
- `CostOptimizationSection.tsx`

### 4.4 Localización

- Catálogo centralizado en `frontend/src/i18n/spanish.ts` con auditoría automatizada (`FORBIDDEN_ENGLISH_UI_PATTERNS`).
- **74 tests frontend pasando**; integración de localización en Analytics y Audit.
- **Residual en inglés / técnico:**
  - `aiCosts.subtitle`: «Executive Response Engine», «LLM»
  - `operationalAuditApi.ts`: error «coverage gaps»
  - Acrónimos: GPT, Claude, Ollama, D365, EEP, EKO/ERO (aceptables en contexto técnico; evaluar para audiencia puramente ejecutiva)
  - Valores crudos del backend en paneles de evidencia/semántica (`execution_strategy`, `verb_id`)

---

## 5. Observabilidad

### 5.1 Capas de métricas

| Capa | Persistencia | Consumida en UI |
|------|--------------|-----------------|
| `performance_metrics` (PostgreSQL) | Permanente | Analytics, Audit, Rendimiento |
| Módulos `*/metrics.py` (12 archivos) | Memoria (hasta restart) | Parcial en `/api/metrics/summary` |
| `performanceStore` (localStorage) | Navegador | Rendimiento (métricas locales) |
| LLM orchestration metrics | Memoria | Costos IA |

### 5.2 Métricas duplicadas o inconsistentes

| Problema | Detalle |
|----------|---------|
| `executive_reasoning_requests` = `llm_requests` | Asignación duplicada en `metrics_service.py` |
| Dos APIs de performance | `/api/metrics/performance` vs `/api/analytics/performance` — mismos datos, schemas distintos |
| Top queries duplicado | `/api/metrics/top-queries` vs `/api/analytics/top-queries` |
| Summary vs report | ~40 campos repetidos entre `MetricsService` y `BusinessAnalyticsService` |
| `route_type` = `handled_by` | Redundancia en DB |
| `/api/metrics/routing` | **Sin consumidor frontend** |
| `/api/analytics/report` | **Fetcheado pero no mostrado** |
| Métricas enterprise en summary | Entidades, ontología, knowledge, reasoning — **no visibles en UI** |
| Requests fallidos | No se persisten métricas cuando hybrid lanza excepción |

### 5.3 Tooltips ejecutivos

Presentes en `METRIC_TOOLTIPS` para cobertura, brecha, éxito, tiempos y costos. Cobertura parcial — muchas métricas del summary carecen de tooltip en UI porque no se renderizan.

---

## 6. Business Knowledge

### 6.1 Inventario `knowledge_pack/`

| Categoría | Contenido | API | Integrado al chat |
|-----------|-----------|-----|:-----------------:|
| concepts/ | 30 archivos | ✅ | ❌ |
| rules/ | 42 archivos | ✅ | ❌ |
| faq/ | ~80+ Q&A | ✅ | ❌ |
| glossary/ | 50 términos | ✅ | ❌ |
| scenarios/ | 20 escenarios | ✅ | ❌ |
| executive/ | 4 perfiles | ❌ endpoint dedicado | ❌ |
| examples/ | 7 ejemplos | Búsqueda | ❌ |

### 6.2 Identidad

- `product_identity/` responde en hybrid con strings en `profile.py`.
- FAQ del pack tiene contenido alineado (Olnatura Intelligence) pero **no se lee en runtime**.
- Duplicación conceptual entre FAQ, product_identity y capability_discovery v2.

### 6.3 Vacíos para demo ejecutiva

1. Reglas de exclusión (cuentas contables en rankings) no aplicadas automáticamente en respuestas.
2. Escenarios (liquidez, concentración, cobranza) sin query types ni ruta executive automática.
3. Perfiles ejecutivos (`director-financiero.md`, etc.) sin consumidor.
4. Capability v2 promete «KPIs» e «Insights» sin backend equivalente.
5. Sin pantalla de Knowledge Pack en frontend.

---

## 7. Inteligencia empresarial

### 7.1 Capacidades reales vs prometidas

| Pregunta típica | Resultado esperado en hybrid |
|-----------------|----------------------------|
| ¿Cuántos clientes existen? | ✅ business_pipeline |
| ¿Qué proveedor tuvo más movimiento en junio? | ✅ (con slot mes si falta) |
| ¿Qué puedes hacer? | product_identity (no discovery) |
| ¿Qué es un proveedor? | legacy_chat (no FAQ) |
| ¿Qué pasó en junio? | guided_fallback / legacy |
| Evaluar riesgos del cliente X | executive_reasoning (si UNSUPPORTED + verbo) |
| ¿Cuánto vendimos en junio? | UNSUPPORTED → fallback |

### 7.2 Verbos ejecutivos (AI Orchestration)

`evaluar`, `diagnosticar`, `justificar`, `recomendar`, `priorizar`, `interpretar` — activan rama executive solo si el planner devuelve `UNSUPPORTED`.

### 7.3 Limitaciones actuales

- LLM por defecto: `LLM_PROVIDER=mock` — demo de síntesis ejecutiva requiere configurar OpenAI/Claude/Ollama.
- Hallucination guard activo si EKO/ERO faltan en paquete de evidencia.
- Memoria conversacional volátil (v1 in-process).
- Sin RAG del knowledge pack en prompts.

---

## 8. Costos

- Panel `/costos-ia` operativo con `/api/ai-costs/summary`.
- Costos estimados por proveedor (GPT, Claude, Ollama) en analítica financiera.
- `aiAvoidanceRate` mide consultas resueltas sin IA generativa.
- **Riesgo demo:** con provider mock, costos y latencias son simulados — debe declararse en demo ejecutiva.
- Endpoints `executive-response/generate` y `/statistics` sin UI dedicada.

---

## 9. Seguridad

| Control | Estado | Severidad |
|---------|--------|-----------|
| Autenticación / autorización | **Ausente** en todos los endpoints | 🔴 Crítica |
| CORS | No configurado en `main.py` | 🟠 Media |
| `POST /upload` | Sin auth; escribe a `data/raw/` | 🔴 Crítica |
| API keys LLM | Solo servidor (`settings.py`) — correcto | ✅ |
| `.env.example` | Contiene `DATABASE_PASSWORD=Olnatura.25` — **parece credencial real** | 🔴 Crítica |
| Variables LLM en `.env.example` | No documentadas (`OPENAI_API_KEY`, etc.) | 🟠 Media |
| Preguntas de usuario en DB | Expuestas en `/api/audit/*`, top-queries | 🟠 Media (PII) |
| Logging estructurado | **Ausente** en `app/` | 🟠 Media |
| Errores silenciados | `metrics_service.py` — `except Exception: pass` | 🟠 Media |
| Rate limiting LLM | Ausente | 🟠 Media |
| OpenAPI `/docs` | Expuesto por defecto | 🟡 Baja |

---

## 10. Experiencia de usuario

### Fortalezas (product polish v1)

- Identidad **Olnatura Intelligence** en hybrid.
- Panel **Resumen de la respuesta** (canal, confianza, evidencia, limitaciones, tiempo).
- Localización mayoritaria en español.
- Sugerencias filtradas (sin gráficas/predicciones).

### Debilidades

- Tres respuestas distintas según redacción de pregunta de capacidades.
- Sugerencias iniciales incluyen «¿Qué pasó en junio?» y «¿Quién es nuestro mejor cliente?» — cobertura parcial.
- 13 ítems en sidebar — puede abrumar en demo; varias pantallas son técnicas (ontología, intención semántica).
- `/rendimiento` mezcla métricas reales y estimaciones locales sin reconciliación clara.

---

## 11. Rendimiento y escalabilidad

| Aspecto | Evaluación |
|---------|------------|
| Latencia consultas deterministas | Baja — tablas resumen / KPIs materializados |
| Latencia executive reasoning | Alta — build EEP + LLM; depende de provider |
| Memoria | Conversation memory in-process; métricas in-memory por worker |
| Persistencia métricas | PostgreSQL para requests hybrid |
| Escalabilidad horizontal | **Limitada** — memoria conversacional no compartida entre workers |
| Costos IA | Controlables con provider mock; reales con API keys |

---

## 12. Pruebas — Resultados verificados (23-jun-2026)

| Suite | Resultado |
|-------|-----------|
| Backend pytest | **690 passed**, 0 failed |
| Cobertura `app/` | **85%** (9.599 stmts, 1.392 miss) |
| Frontend vitest | **74 passed** (19 archivos) |
| Integración | 18 archivos; requiere PostgreSQL |

### Módulos con cobertura ≥ 90% (muestra)

`product_identity` (98%), `slot_clarification` (100%), `suggested_questions/validator` (97%), `evidence_package` (alto), `ai_orchestration` (alto).

### Módulos con cobertura baja (riesgo)

`temporal_resolver` (25%), `upload_service` (45%), legacy chat layers (variable).

### Huecos de tests

- Sin tests UI para `PerformancePage`, `AnalyticsPage`, `AICostsPage`.
- Scripts manuales `scripts/test_*.py` fuera de CI.
- `pytest-cov` no en `requirements.txt` (instalación adicional).

---

## 13. Lista priorizada de hallazgos

### 🔴 Problemas críticos (bloquean piloto externo)

| # | Problema | Impacto |
|---|----------|---------|
| C1 | API sin autenticación | Cualquier actor puede chat, upload, métricas, LLM |
| C2 | `POST /upload` abierto | Vector de ataque / sobrescritura en `data/raw/` |
| C3 | Credencial en `.env.example` | Exposición de contraseña aparentemente real |
| C4 | Knowledge pack desconectado del chat | FAQ y reglas no aplican en respuestas reales |
| C5 | Preguntas de usuario persistidas sin control de acceso | Riesgo PII en audit/top-queries |

### 🟠 Problemas importantes (afectan demo y confianza)

| # | Problema | Impacto |
|---|----------|---------|
| I1 | Triple canal de capacidades (identity / discovery / pipeline) | Respuestas inconsistentes en demo |
| I2 | Sugerencias frontend con preguntas no soportadas | Frustración del usuario ejecutivo |
| I3 | Executive reasoning solo en UNSUPPORTED + verbo | EKO/ERO invisibles en consultas SQL |
| I4 | Memoria conversacional volátil | Follow-ups fallan tras restart |
| I5 | Observabilidad fragmentada y duplicada | Métricas confusas para dirección |
| I6 | LLM mock por defecto | Síntesis ejecutiva no es real sin configuración |
| I7 | Sin logging estructurado | Imposible diagnosticar incidentes en piloto |
| I8 | ~40 endpoints sin UI ni deprecación documentada | Superficie de mantenimiento |

### 🟡 Micromejoras

| # | Mejora |
|---|--------|
| M1 | Traducir error «coverage gaps» en `operationalAuditApi.ts` |
| M2 | Eliminar o usar componentes huérfanos de rendimiento |
| M3 | Renderizar `/api/analytics/report` o dejar de fetchearlo |
| M4 | Exponer `/api/metrics/routing` o deprecar |
| M5 | Documentar vars LLM en `.env.example` |
| M6 | Añadir `pytest-cov` a requirements de desarrollo |
| M7 | Pantalla o sección de Knowledge Pack para demo de conocimiento |

### Deuda técnica restante

- Unificación de motores determinísticos y parsers semánticos.
- Deprecación progresiva de `/api/chat` legacy.
- Consolidación analytics (datamart vs business_analytics vs metrics).
- Separación `requirements.txt` prod vs dev.
- Tipos TypeScript `MetricsSummary` desactualizados vs backend (~50 campos).

### Funcionalidades pendientes

- Query types: SUM, TREND, COMPARE, actividad temporal genérica.
- Integración knowledge_pack → guided fallback / definiciones.
- Pantalla Knowledge Pack.
- AuthN/AuthZ.
- Conversation memory persistente (Redis/DB).
- Rate limiting en endpoints LLM.

### Riesgos para una demostración con Dirección

| Riesgo | Mitigación en demo |
|--------|-------------------|
| Pregunta fuera de cobertura («¿Qué pasó en junio?») | Usar guion con 5–7 preguntas validadas |
| Tres respuestas distintas a «capacidades» | Estandarizar frase: «¿Qué puedes hacer?» |
| Executive reasoning con mock LLM | Configurar provider real o declarar modo simulado |
| Sidebar con 13 secciones técnicas | Recorrido guiado: Asistente → Analytics → Audit → Costos IA |
| Restart del servidor pierde memoria | Demo en sesión única continua |
| Ontología/Evidencia muestran acrónimos técnicos | Preparar narrativa de «capas de evidencia» |
| Sin auth — acceso abierto en red | Demo solo en red interna / localhost |

---

## 14. Respuestas finales

### ¿Está listo para una prueba real con usuarios?

**No en su estado actual** para usuarios externos o multi-tenant.

Requiere como mínimo: autenticación, cierre de upload, rotación de credenciales en ejemplos, logging, y alineación sugerencias ↔ capacidades reales. Con un **piloto interno cerrado** (5–10 usuarios, red privada, guion de preguntas, PostgreSQL estable), puede ejecutarse con supervisión técnica.

### ¿Está listo para una demo con Dirección?

**Sí, con guion controlado y preparación previa.**

La plataforma ofrece narrativa completa (asistente, analítica, auditoría, costos IA, capas enterprise) y identidad de producto pulida. La demo debe evitar preguntas fuera de cobertura, declarar limitaciones del provider LLM, y enfocarse en consultas deterministas verificables y 1–2 ejemplos de razonamiento ejecutivo con datos EKO/ERO cargados.

### ¿Qué tres mejoras aportarían mayor valor antes de pasar a producción?

1. **Seguridad mínima viable:** autenticación (API key o SSO) en chat, métricas, audit, upload y executive-response; rotar credencial de `.env.example`; CORS restrictivo.
2. **Conectar knowledge_pack al runtime conversacional:** responder definiciones y FAQ desde el pack antes de legacy LLM; unificar respuestas de capacidades en un solo canal determinista.
3. **Alinear promesa ↔ capacidad real:** ajustar sugerencias UI, capability discovery v2 y guion de demo a los 10 query types soportados; persistir memoria conversacional o documentar limitación explícitamente en UI.

---

## Anexo A — Candidatos a eliminación o consolidación (solo identificación)

> **No ejecutar eliminación automática.** Validar con stakeholders antes de cada acción.

| Candidato | Acción sugerida | Prioridad |
|-----------|-----------------|-----------|
| Componentes `PerformanceHero`, `PerformanceMetricsGrid`, `CostOptimizationSection` | Eliminar o integrar en `PerformancePage` | Baja |
| `get_conversation_memory_service()` huérfano | Eliminar factory | Baja |
| Endpoints datamart legacy | Deprecar y documentar; mantener si hay consumidor BI | Media |
| `/api/semantic/*`, `/api/query/*` | Mover detrás de flag DEBUG o documentar como ops | Media |
| Pipeline legacy completo | Deprecar tras migrar delegaciones a hybrid | Alta (largo plazo) |
| Duplicado `DeterministicResponseEngine` | Consolidar en un módulo | Alta (largo plazo) |
| `knowledge_pack` vs `enterprise_knowledge` | Definir fuente de verdad única o puente explícito | Alta |

---

## Anexo B — Comandos de verificación reproducibles

```powershell
# Backend
python -m pytest tests/ -q
python -m pytest tests/ --cov=app --cov-report=term-missing -q

# Frontend
cd frontend
npm test -- --run
```

**Resultados de esta auditoría:** 690 passed (backend), 85% cobertura `app/`, 74 passed (frontend).

---

*Informe generado por auditoría de arquitectura, revisión enterprise y QA. Sin modificaciones al código fuente.*
