# Business Query Engine v1

## Objetivo

Primer **Business Query Engine** del Asistente de Inteligencia Empresarial Olnatura.

Convierte un `BusinessSemanticIntent` (producido por el Semantic Intent Builder) en un `BusinessQuery` tipado y auditable, listo para ser ejecutado en sprints futuros por templates SQL parametrizados.

Este sprint es **planificación únicamente**: no ejecuta consultas, no accede a PostgreSQL y no genera SQL dinámico.

## Arquitectura

```
Pregunta (texto)
      │
      ▼
SemanticIntentBuilder
      │
      ▼
BusinessSemanticIntent
      │
      ▼
BusinessQueryPlanner
      │
      ▼
BusinessQuery
  • query_type
  • filters
```

### Componentes

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Tipos | `app/query_engine/query_types.py` | Enum `BusinessQueryType` |
| Modelo | `app/query_engine/business_query.py` | Contrato `BusinessQuery` |
| Planner | `app/query_engine/query_planner.py` | Reglas intent → query |
| API | `app/api/routes/query.py` | Endpoint de prueba `/api/query/plan` |

## Query Planner

`BusinessQueryPlanner.plan(intent)` evalúa reglas determinísticas en orden:

| # | Condición | `query_type` |
|---|-----------|--------------|
| 1 | `COUNT` + `CLIENTE` | `COUNT_CLIENTES` |
| 2 | `COUNT` + `PROVEEDOR` | `COUNT_PROVEEDORES` |
| 3 | `TOP` + `CLIENTE` | `TOP_CLIENTES` |
| 4 | `TOP` + `PROVEEDOR` | `TOP_PROVEEDORES` |
| 5 | `MAX` + `PROVEEDOR` + `filters.mes` | `MAX_PROVEEDOR_MES` |
| 6 | `MAX` + `TRANSACCION` + `filters.cliente_codigo` | `MAX_TRANSACCION_CLIENTE` |
| 7 | `LOOKUP` + `CLIENTE` + `CUENTA` (source) | `LOOKUP_CLIENTE_BY_CUENTA` |
| — | Cualquier otro caso | `UNSUPPORTED` |

Los filtros del intent se serializan en `filters` excluyendo valores nulos.

## Query templates (futuro)

Cada `BusinessQueryType` mapeará a un template SQL fijo en el siguiente sprint:

| `query_type` | Template futuro (conceptual) |
|--------------|------------------------------|
| `COUNT_CLIENTES` | `SELECT COUNT(*) FROM clientes WHERE ...` |
| `COUNT_PROVEEDORES` | `SELECT COUNT(*) FROM proveedores WHERE ...` |
| `TOP_CLIENTES` | `SELECT ... FROM clientes ORDER BY ... LIMIT N` |
| `TOP_PROVEEDORES` | `SELECT ... FROM proveedores ORDER BY ... LIMIT N` |
| `MAX_PROVEEDOR_MES` | Ranking proveedor por movimiento filtrado por mes |
| `MAX_TRANSACCION_CLIENTE` | Transacción máxima por `cliente_codigo` |
| `LOOKUP_CLIENTE_BY_CUENTA` | Resolver cliente a partir de `cuenta_codigo` |
| `UNSUPPORTED` | Sin template; respuesta controlada al usuario |

Los templates serán **estáticos y parametrizados** — sin Text-to-SQL ni SQL dinámico.

## Endpoint de prueba

```
GET /api/query/plan?question=¿Cuántos clientes existen?
```

Respuesta:

```json
{
  "query_type": "COUNT_CLIENTES",
  "filters": {}
}
```

## Ejemplos

| Pregunta | `query_type` |
|----------|--------------|
| ¿Cuántos clientes existen? | `COUNT_CLIENTES` |
| ¿Qué proveedor tuvo más movimiento en junio? | `MAX_PROVEEDOR_MES` |
| ¿Cuál fue la transacción más alta del cliente C001? | `MAX_TRANSACCION_CLIENTE` |
| ¿De qué cliente es la cuenta IMA0709183? | `LOOKUP_CLIENTE_BY_CUENTA` |

## Limitaciones actuales

- Solo planifica; no ejecuta ni devuelve datos.
- Cobertura limitada a 7 tipos de consulta + `UNSUPPORTED`.
- Intents sin regla explícita (p. ej. actividad de proveedores por año) devuelven `UNSUPPORTED`.
- Los filtros se propagan tal cual; no hay validación de negocio sobre códigos o rangos.
- No integrado al chat ni al pipeline de respuestas determinísticas.

## Evolución futura

1. **Query Templates** — Archivos SQL estáticos por `BusinessQueryType`.
2. **Query Executor** — Ejecutar templates contra PostgreSQL vía SQLAlchemy.
3. **Repositorios** — Capa de acceso a datos del data mart Olnatura.
4. **Ampliar planner** — Más combinaciones operación × entidad (`SUM`, `TREND`, `AVG`, etc.).
5. **Integración con chat** — Pipeline completo: pregunta → intent → query → resultado → respuesta.
6. **Telemetría** — Medir tasa de `UNSUPPORTED` para priorizar nuevas reglas.

## Pruebas

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/test_query_planner.py -v --cov=app.query_engine --cov-report=term-missing
```

Cobertura mínima del sprint: **90%** del módulo `app/query_engine`.
