# Business Query Executor v1

## Objetivo

Primer **Business Query Executor** del Asistente de Inteligencia Empresarial Olnatura.

Convierte un `BusinessQuery` (producido por el Query Planner) en un `BusinessQueryResult` estructurado consultando el **Data Mart** de forma determinística, sin SQL dinámico ni Text-to-SQL.

Este sprint **ejecuta consultas aprobadas** pero no genera narrativas ni integra con el chat.

## Arquitectura

```
Pregunta (texto)
      │
      ▼
SemanticIntentBuilder
      │
      ▼
BusinessQueryPlanner
      │
      ▼
BusinessQuery
      │
      ▼
BusinessQueryExecutor
      │
      ├─ ClienteRepository
      └─ ProveedorRepository
      │
      ▼
BusinessQueryResult
  • query_type
  • success
  • data
  • metadata
```

### Componentes

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Resultado | `app/query_executor/query_result.py` | Contrato `BusinessQueryResult` |
| Executor | `app/query_executor/business_query_executor.py` | Mapping query_type → repository |
| Repositorio | `app/repositories/query_executor/cliente_repository.py` | Consultas sobre clientes |
| Repositorio | `app/repositories/query_executor/proveedor_repository.py` | Consultas sobre proveedores |
| API | `app/api/routes/query.py` | Endpoint `/api/query/execute` |

## Flujo

1. El endpoint recibe `question`.
2. `SemanticIntentBuilder` produce `BusinessSemanticIntent`.
3. `BusinessQueryPlanner` produce `BusinessQuery`.
4. `BusinessQueryExecutor` ejecuta el mapping aprobado.
5. Los repositories consultan tablas/vistas del Data Mart.
6. Se devuelve `BusinessQueryResult` con datos serializados.

## Repositories

### ClienteRepository

| Método | Tabla/Vista | Descripción |
|--------|-------------|-------------|
| `count_clientes()` | `fact_cliente` | Conteo total de clientes |
| `top_clientes(limit)` | `mv_top_clientes` | Ranking de clientes |

### ProveedorRepository

| Método | Tabla/Vista | Descripción |
|--------|-------------|-------------|
| `count_proveedores()` | `fact_proveedor` | Conteo total de proveedores |
| `top_proveedores(limit)` | `mv_top_proveedores` | Ranking de proveedores |
| `max_proveedor_mes(mes, anio?)` | `fact_proveedor_mes` | Proveedor con mayor movimiento en el mes |

### Tablas permitidas

- `fact_cliente`
- `fact_proveedor`
- `mv_top_clientes`
- `mv_top_proveedores`
- `fact_proveedor_mes`

**No se utiliza** `movimientos_diario` ni tablas fuera del Data Mart.

## Executor — mapping aprobado

| `query_type` | Repository | `data` |
|--------------|------------|--------|
| `COUNT_CLIENTES` | `count_clientes()` | `{"total": N}` |
| `COUNT_PROVEEDORES` | `count_proveedores()` | `{"total": N}` |
| `TOP_CLIENTES` | `top_clientes()` | `{"items": [...]}` |
| `TOP_PROVEEDORES` | `top_proveedores()` | `{"items": [...]}` |
| `MAX_PROVEEDOR_MES` | `max_proveedor_mes(mes)` | registro del proveedor líder |
| Otro caso | — | `success=false` |

## Endpoint de prueba

```
GET /api/query/execute?question=¿Cuántos clientes existen?
```

Respuesta:

```json
{
  "query_type": "COUNT_CLIENTES",
  "success": true,
  "data": {
    "total": 50
  },
  "metadata": {
    "filters": {}
  }
}
```

## Ejemplos

| Pregunta | `query_type` | Resultado |
|----------|--------------|-----------|
| ¿Cuántos clientes existen? | `COUNT_CLIENTES` | `total` |
| ¿Cuántos proveedores existen? | `COUNT_PROVEEDORES` | `total` |
| Muéstrame los principales clientes | `TOP_CLIENTES` | `items` |
| ¿Qué proveedor tuvo más movimiento en junio? | `MAX_PROVEEDOR_MES` | proveedor + métricas |

## Restricciones

- SQL estático y explícito en cada repository; sin Query Builder dinámico.
- Sin LLM, Ollama ni embeddings.
- Sin integración con chat ni narrativas.
- Tipos no mapeados (`UNSUPPORTED`, `MAX_TRANSACCION_CLIENTE`, `LOOKUP_CLIENTE_BY_CUENTA`) devuelven `success=false`.
- `Decimal` y fechas se serializan a `float` / ISO-8601 en los resultados.

## Pruebas

Unitarias (repositories mockeados):

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/test_business_query_executor.py -v --cov=app.query_executor --cov-report=term-missing
```

Integración (requiere PostgreSQL con Data Mart):

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/integration/test_query_executor_integration.py -v -m integration
```

Cobertura mínima del executor: **90%**.

## Evolución futura

1. Templates SQL dedicados por `query_type` en archivos separados.
2. Soporte para `MAX_TRANSACCION_CLIENTE` y `LOOKUP_CLIENTE_BY_CUENTA`.
3. **Deterministic Response Engine** — convertir `BusinessQueryResult` en texto natural.
4. Integración con el pipeline de chat.
5. Caché de resultados frecuentes (`COUNT_*`, `TOP_*`).
