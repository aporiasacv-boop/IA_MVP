# Enterprise Evidence Package v1

## Objetivo

Contrato definitivo RAG para consumo por cualquier LLM. El **Enterprise Evidence Package (EEP)** ensambla únicamente el conocimiento necesario para responder una pregunta — sin SQL embebido, sin narrativa, sin llamadas a LLM.

## Arquitectura

```
Pregunta
    ↓
Semantic Business Execution Planner (SBEP)
    ↓
Evidence Package Builder
    ├── Enterprise Knowledge Object (EKO)
    └── Enterprise Reasoning Object (ERO)
    ↓
Enterprise Evidence Package (EEP)
    ↓
(futuro) LLM / RAG
```

## Flujo completo

1. Usuario envía pregunta a `POST /api/evidence/build`
2. SBEP genera `BusinessExecutionPlan` (verbo, objetos, estrategia, secciones requeridas)
3. Se resuelve `canonical_id` desde entity hints o parámetro explícito
4. Se cargan EKO y ERO persistidos (JSONB — nunca SQL en el paquete)
5. Evidence Builder filtra secciones según `required_knowledge` y `required_reasoning`
6. Se calculan limitaciones, confidence y metadata
7. Se retorna EEP estructurado

## Contrato EEP

| Sección | Contenido |
|---------|-----------|
| `question` | Pregunta original |
| `execution_plan` | Plan SBEP completo |
| `business_context` | Contexto, objetos, hints, canonical_id |
| `knowledge` | Items EKO seleccionados |
| `reasoning` | Conclusiones ERO seleccionadas |
| `facts` | Hechos verificables |
| `signals` | Señales EKO + ERO |
| `alerts` | Alertas |
| `recommendations` | Recomendaciones ERO |
| `evidence` | Índice combinado EKO + ERO |
| `limitations` | Gaps y restricciones |
| `confidence` | Agregado con trazabilidad |
| `metadata` | Versión, flags determinísticos |

### EvidenceItem

- `key`, `value`, `source`, `evidence`, `confidence`, `timestamp`

## API

```
POST /api/evidence/build
GET  /api/evidence/schema
GET  /api/evidence/statistics
GET  /api/evidence/example
```

## Ciclo de construcción

Idempotente por pregunta + entidad: misma entrada produce mismo ensamblaje (salvo timestamps).

## Cómo añadir nuevas fuentes de evidencia

1. Extender EKO o ERO con nuevas secciones (sprints anteriores)
2. Actualizar `EKO_SECTION_MAP` / `ERO_SECTION_MAP` en `evidence_builder.py`
3. Mapear secciones en SBEP `required_knowledge` / `required_reasoning`
4. No se requiere modificar el contrato EEP base

## Observabilidad

- `evidence_packages_total`
- `average_package_size` (bytes JSON)
- `average_evidence_items`
- `average_evidence_confidence`
- `missing_evidence`
- `package_build_time`

## UI

Ruta `/evidencia` — exploración de paquetes construidos.

## Garantías

- `metadata.deterministic = true`
- `metadata.contains_sql = false`
- `metadata.contains_llm_output = false`
- Sin integración LLM en este sprint
