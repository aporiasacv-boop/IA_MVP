# Catálogo de API — RC1

**Total endpoints:** 99 (incluye `POST /upload`)  
**Routers registrados en `main.py`:** 29

---

## Clasificación

| Clase | Descripción |
|-------|-------------|
| **PRODUCCIÓN** | Consumido por UI activa o canal principal |
| **INTERNA** | Health, version, métricas de sistema |
| **LEGACY** | Mantenido por compatibilidad; UI migrada |
| **DEBUG** | Upload, endpoints de desarrollo |
| **EXPERIMENTAL** | Query API directa, insights |

---

## Producción (52 endpoints con UI o pipeline principal)

### Chat y asistente

| Método | Ruta | Clase |
|--------|------|-------|
| POST | `/api/chat/hybrid` | PRODUCCIÓN |

### Métricas y analítica

| Método | Ruta | Clase |
|--------|------|-------|
| GET | `/api/metrics/summary` | PRODUCCIÓN |
| GET | `/api/metrics/top-queries` | PRODUCCIÓN |
| GET | `/api/metrics/performance` | PRODUCCIÓN |
| GET | `/api/metrics/routing` | PRODUCCIÓN |
| GET | `/api/analytics/coverage` | PRODUCCIÓN |
| GET | `/api/analytics/performance` | PRODUCCIÓN |
| GET | `/api/analytics/financial` | PRODUCCIÓN |
| GET | `/api/analytics/top-queries` | PRODUCCIÓN |
| GET | `/api/analytics/handled-by` | PRODUCCIÓN |

### Auditoría y entidades

| Método | Ruta | Clase |
|--------|------|-------|
| GET | `/api/audit/*` (7) | PRODUCCIÓN |
| GET | `/api/business-entities/*` (3) | PRODUCCIÓN |
| GET | `/api/canonical-entities/*` (3) | PRODUCCIÓN |
| GET | `/api/entity-profiles/*` (3) | PRODUCCIÓN |
| GET | `/api/business-ontology/*` (4) | PRODUCCIÓN |

### Conocimiento y razonamiento

| Método | Ruta | Clase |
|--------|------|-------|
| GET | `/api/enterprise-knowledge/*` (4) | PRODUCCIÓN |
| GET | `/api/business-knowledge/*` (4) | PRODUCCIÓN |
| GET | `/api/knowledge/*` (4) | PRODUCCIÓN |
| GET | `/api/reasoning/*` (4) | PRODUCCIÓN |
| GET | `/api/semantic-intent/*` (4) | PRODUCCIÓN |
| GET | `/api/evidence/*` (4) | PRODUCCIÓN |

### FinOps, simulación, decisiones

| Método | Ruta | Clase |
|--------|------|-------|
| GET | `/api/finops/overview` | PRODUCCIÓN |
| GET | `/api/finops/costs` | PRODUCCIÓN |
| GET | `/api/finops/providers` | PRODUCCIÓN |
| GET | `/api/finops/forecast` | PRODUCCIÓN |
| GET | `/api/finops/savings` | PRODUCCIÓN |
| GET | `/api/finops/trends` | PRODUCCIÓN |
| GET | `/api/finops/health` | PRODUCCIÓN |
| GET/POST | `/api/simulation/*` (4) | PRODUCCIÓN |
| GET/POST | `/api/decision/*` (4) | PRODUCCIÓN |

### Respuesta ejecutiva

| Método | Ruta | Clase |
|--------|------|-------|
| GET/POST | `/api/executive-response/*` (5) | PRODUCCIÓN |

---

## Interna (2)

| Método | Ruta |
|--------|------|
| GET | `/health` |
| GET | `/version` |

---

## Legacy (25)

| Método | Ruta | Notas |
|--------|------|-------|
| POST | `/api/chat` | Chat legacy |
| GET | `/api/kpis` + 8 rutas datamart | Sin UI |
| GET | `/api/ai-costs/summary` | Reemplazado por FinOps en UI |
| GET | `/api/knowledge-pack/*` (6) | Facade EKS |
| GET | `/api/insights/*` (2) | Scripts |
| GET | `/api/metadata` | Scripts |

---

## Experimental / debug (20)

| Método | Ruta | Notas |
|--------|------|-------|
| POST | `/upload` | Carga archivos |
| POST/GET | `/api/query/*` (3) | Query engine directo |
| GET | `/api/semantic/*` (3) | Búsqueda semántica |

---

## Verificación RC1

| Criterio | Estado |
|----------|--------|
| Sin duplicados de path+método | ✅ |
| Rutas inaccesibles (404 en registro) | ✅ Ninguna detectada |
| Endpoints muertos sin tests | ⚠️ `/api/insights`, `/api/metadata` — solo scripts |
| Frontend conectado a backend real | ✅ 16 pantallas |

---

## Mapa frontend → API

| Pantalla | APIs principales |
|----------|------------------|
| Asistente | `POST /api/chat/hybrid` |
| Rendimiento | `/api/metrics/*` |
| Analítica | `/api/analytics/*` |
| Auditoría | `/api/audit/*` |
| Entidades | `/api/business-entities/*` |
| Canónicas | `/api/canonical-entities/*` |
| Perfiles | `/api/entity-profiles/*` |
| Ontología | `/api/business-ontology/*` |
| Conocimiento | `/api/enterprise-knowledge/*`, `/api/business-knowledge/*` |
| Objetos EKO | `/api/knowledge/*` |
| Razonamiento | `/api/reasoning/*` |
| Intención | `/api/semantic-intent/*` |
| Evidencia | `/api/evidence/*` |
| Simulador | `/api/simulation/*` |
| Centro Decisiones | `/api/decision/*` |
| FinOps | `/api/finops/*` |
