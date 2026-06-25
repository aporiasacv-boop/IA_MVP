# Enterprise Knowledge Object v1

## Objetivo

Contrato oficial de conocimiento empresarial estructurado para consumo por Intent Engine, Executive Reasoning y LLM — **sin SQL, sin narrativa, sin output de IA**.

## Pipeline

```
business_entity_master ──┐
canonical_business_entity ──┤
business_entity_profile ──┼──► Knowledge Builder ──► enterprise_knowledge_object (JSONB)
business_ontology ────────┘
```

## Estructura del objeto (EKO v1)

| Sección | Contenido |
|---------|-----------|
| `identity` | Identidad canónica + alias estructurales |
| `roles` | Clasificaciones de rol (ontología) |
| `nature` | Naturaleza contable sugerida |
| `behaviors` | Patrones de participación |
| `facts` | Métricas verificables del perfil |
| `signals` | Señales derivadas (volumen, estacionalidad) |
| `alerts` | Anomalías (sin perfil, roles ambiguos) |
| `patterns` | Distribución mensual y patrones temporales |
| `relationships` | Cuentas y contrapartes top |
| `quality` | Completitud y confianza agregada |
| `evidence` | Índice de evidencias ontológicas |
| `metadata` | Versión, fuentes, flags determinísticos |

## KnowledgeItem (elemento atómico)

Cada elemento incluye:

- `key` — identificador del hecho
- `value` — dato estructurado (nunca narrativa)
- `source` — capa de origen (`business_entity_master`, `canonical_business_entity`, `business_entity_profile`, `business_ontology`)
- `evidence` — referencia verificable
- `confidence` — 0.0 a 1.0
- `computed_at` — timestamp de cálculo

## API

```
GET /api/knowledge/entities
GET /api/knowledge/entities/{canonical_id}
GET /api/knowledge/statistics
GET /api/knowledge/schema
```

## Construcción idempotente

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe scripts\build_enterprise_knowledge.py
```

## Garantías del contrato

- `metadata.contains_sql = false`
- `metadata.contains_llm_output = false`
- `metadata.deterministic = true`
- Sin consultas SQL embebidas
- Sin texto generado por IA

## UI

Ruta `/conocimiento` — exploración de identidad, ontología, hechos, señales, alertas y evidencia.

## Observabilidad

- `knowledge_objects_total`
- `knowledge_build_time`
- `knowledge_average_completeness`
- `knowledge_average_confidence`
- `knowledge_last_refresh`

Expuestas en `/api/metrics/summary` y `/api/analytics/report`.

## Health checks

El servicio valida:

| Invariante | Descripción |
|------------|-------------|
| Objetos incompletos | `completeness < 0.3` (informativo) |
| Evidencia inexistente | `evidence[]` vacío |
| Confidence inválido | Fuera de rango [0, 1] |
| Secciones vacías | Sin `facts` ni `identity.items` |
| Relaciones rotas | `relationships` sin perfil subyacente |
| Hechos contradictorios | Alerta `conflicting_natures` |

## Ejemplo de contrato JSON

```json
{
  "schema_version": "1.0.0",
  "canonical_id": 42,
  "identity": {
    "canonical_id": 42,
    "canonical_name": "WALMART",
    "normalized_name": "WALMART",
    "primary_rfc": "NWM9709244",
    "alias_count": 2,
    "aliases": [],
    "items": [
      {
        "key": "canonical_name",
        "value": "WALMART",
        "source": "canonical_business_entity",
        "evidence": {"field": "canonical_name", "canonical_id": 42},
        "confidence": "1.0000",
        "computed_at": "2026-06-24T12:00:00"
      }
    ]
  },
  "roles": [],
  "nature": [],
  "behaviors": [],
  "facts": [],
  "signals": [],
  "alerts": [],
  "patterns": [],
  "relationships": [],
  "quality": {
    "completeness": "0.8571",
    "average_confidence": "0.8200",
    "has_profile": true,
    "has_ontology": true,
    "ontology_assignment_count": 3,
    "items": []
  },
  "evidence": [],
  "metadata": {
    "schema_id": "enterprise_knowledge_object_v1",
    "built_at": "2026-06-24T12:00:00",
    "sources": ["business_entity_master", "canonical_business_entity", "business_entity_profile", "business_ontology"],
    "deterministic": true,
    "contains_sql": false,
    "contains_llm_output": false
  }
}
```

## Tabla de persistencia

`enterprise_knowledge_object`:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `knowledge_id` | serial PK | Identificador del objeto |
| `canonical_id` | int UNIQUE FK | Entidad canónica |
| `knowledge_payload` | jsonb | EKO completo |
| `completeness` | numeric | Completitud agregada |
| `average_confidence` | numeric | Confianza promedio |
| `built_at` | timestamp | Última construcción |
