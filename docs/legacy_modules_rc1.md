# Módulos Legacy — Clasificación RC1

**Fecha:** 2026-06-23  
**Política:** No eliminar automáticamente. Documentar y deprecar en fases posteriores.

---

## Leyenda

| Estado | Significado |
|--------|-------------|
| **ACTIVO** | Runtime principal, consumido por UI o pipeline híbrido |
| **COMPATIBILIDAD** | Facade o API legacy con consumidores activos (tests, scripts, integraciones) |
| **CANDIDATO A ELIMINACIÓN** | Sin consumidores en runtime; eliminación diferida post-piloto |

---

## Backend

| Módulo / superficie | Estado | Consumidores | Notas |
|---------------------|--------|--------------|-------|
| `enterprise_knowledge_service` | ACTIVO | Hybrid chat, UI, EDE | **Fuente canónica de conocimiento** |
| `operational_metrics` | ACTIVO | FinOps UI, Simulation, EDE, hybrid | **Fuente canónica FinOps** |
| `simulation_engine` | ACTIVO | Simulador UI, EDE | **Fuente canónica simulación** |
| `enterprise_decision` | ACTIVO | Centro de Decisiones UI | **Fuente canónica decisiones** |
| `product_identity` | ACTIVO | Hybrid router | Identidad del asistente |
| `capability_discovery` v2 | ACTIVO | Hybrid router | Capacidades del sistema |
| `response_engine` | ACTIVO | Query API, hybrid | Motor determinístico v2 |
| `hybrid_chat` + router | ACTIVO | Asistente UI | **Canal principal** |
| `enterprise_reasoning` | ACTIVO | ERO UI, EEP, EDE | |
| `evidence_package` | ACTIVO | Evidencia UI, EDE | |
| `enterprise_knowledge` (EKO) | COMPATIBILIDAD | `/api/knowledge`, EDE, analytics | Objetos BD; sin UI directa |
| `business_knowledge` | COMPATIBILIDAD | `/api/business-knowledge`, hybrid | Facade sobre EKS |
| `knowledge_pack` | COMPATIBILIDAD | `/api/knowledge-pack` | Facade sobre EKS |
| `business_knowledge/loader,matcher,responder` | COMPATIBILIDAD | Tests, capability tests | Re-exports; runtime usa EKS |
| `knowledge_pack/loader` | COMPATIBILIDAD | Tests | |
| `chat` (`POST /api/chat`) | COMPATIBILIDAD | Tests, integraciones legacy | Delega parcialmente |
| `services/deterministic_response_engine` | COMPATIBILIDAD | Chat legacy | Distinto de `response_engine/` |
| `services/intent_router` | COMPATIBILIDAD | Fallback hybrid | Reemplazado por semantic intent |
| `analytics` (`/api/kpis`) | COMPATIBILIDAD | Scripts ETL | Sin UI frontend |
| `insights`, `metadata` | COMPATIBILIDAD | Scripts | Sin UI |
| `/api/ai-costs` | COMPATIBILIDAD | Ningún frontend RC1 | FinOps lo reemplazó en UI |
| `guided_fallback` v1 | COMPATIBILIDAD | Path de fallback | v2 es principal |
| `services/executive_summary_service` | COMPATIBILIDAD | Script ETL | No runtime FastAPI |

---

## Frontend (eliminados en RC1)

| Artefacto | Estado previo | Acción RC1 |
|-----------|---------------|------------|
| `AICostsPage` | Huérfano | **Eliminado** |
| `aiCostsApi`, `useAICosts` | Huérfano | **Eliminado** |
| `businessKnowledgeApi`, `useBusinessKnowledge` | Huérfano | **Eliminado** |
| `PerformanceHero`, `CostOptimizationSection`, `PerformanceMetricsGrid` | Huérfano | **Eliminado** |

---

## Resumen cuantitativo

| Clasificación | Backend | Frontend |
|---------------|---------|----------|
| ACTIVO | 28 módulos | 16 páginas |
| COMPATIBILIDAD | 9 superficies | 1 alias ruta (`/costos-ia`) |
| CANDIDATO A ELIMINACIÓN (documentado, no eliminado) | 5 submódulos | 0 (limpiados en RC1) |

---

## Plan de deprecación sugerido (post-piloto)

### Fase A — Bajo riesgo
- Retirar `/api/ai-costs` tras confirmar cero consumidores externos
- Eliminar facades `business_knowledge/{loader,matcher,responder}` tras migrar tests a EKS

### Fase B — Medio riesgo
- Unificar `/api/kpis` en `/api/analytics`
- Deprecar `POST /api/chat` → solo `POST /api/chat/hybrid`

### Fase C — Alto riesgo
- Consolidar `DeterministicResponseEngine` (×2)
- Retirar `IntentRouter` tras migración completa a semantic intent
