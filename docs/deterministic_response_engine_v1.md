# Deterministic Response Engine v1

## Objetivo

Primer **Deterministic Response Engine** del pipeline semántico empresarial de Olnatura.

Transforma un `BusinessQueryResult` (datos estructurados del Data Mart) en un `BusinessResponse` legible para el usuario, usando **plantillas determinísticas** sin LLM, Ollama, Qwen ni IA generativa.

Este sprint es **aditivo**: no modifica el `DeterministicResponseEngine` del chat (`app/services/`) ni integra con Ollama.

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
BusinessQueryExecutor
      │
      ▼
BusinessQueryResult
      │
      ▼
DeterministicResponseEngine  (app/response_engine/)
      │
      ▼
BusinessResponse
  • success
  • answer
  • query_type
  • metadata
```

### Componentes

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Contrato | `app/response_engine/response_result.py` | Modelo `BusinessResponse` |
| Templates | `app/response_engine/response_templates.py` | Catálogo de plantillas |
| Motor | `app/response_engine/deterministic_response_engine.py` | Generación determinística |
| API | `app/api/routes/query.py` | Endpoint `/api/query/respond` |

## Templates

| `query_type` | Plantilla |
|--------------|-----------|
| `COUNT_CLIENTES` | Actualmente existen {total} clientes registrados. |
| `COUNT_PROVEEDORES` | Actualmente existen {total} proveedores registrados. |
| `TOP_CLIENTES` | Encabezado + lista numerada de clientes |
| `TOP_PROVEEDORES` | Encabezado + lista numerada de proveedores |
| `MAX_PROVEEDOR_MES` | El proveedor con mayor movimiento... fue {proveedor} con volumen {monto_total} |
| `UNSUPPORTED` | Actualmente no existe una consulta empresarial configurada para esta solicitud. |

### Formato TOP

```
Los principales clientes identificados son:

1. Cliente Uno (C001) — 10 movimientos
2. Cliente Dos (C002) — 8 movimientos
```

## Flujo

1. El endpoint recibe `question`.
2. Se construye el intent semántico.
3. Se planifica la consulta (`BusinessQuery`).
4. Se ejecuta contra el Data Mart (`BusinessQueryResult`).
5. `DeterministicResponseEngine.generate()` selecciona la plantilla según `query_type`.
6. Si `success=false` o el tipo no tiene plantilla, se usa `UNSUPPORTED`.
7. Se devuelve `BusinessResponse` con texto legible.

## Endpoint de prueba

```
GET /api/query/respond?question=¿Cuántos clientes existen?
```

Respuesta:

```json
{
  "success": true,
  "answer": "Actualmente existen 50 clientes registrados.",
  "query_type": "COUNT_CLIENTES",
  "metadata": {
    "query_metadata": {
      "filters": {}
    }
  }
}
```

## Limitaciones actuales

- Solo cubre los `query_type` ejecutados por el Business Query Executor v1.
- `LOOKUP_CLIENTE_BY_CUENTA` y `MAX_TRANSACCION_CLIENTE` aún no tienen plantilla propia.
- Fallos de ejecución (`no_data_for_period`, filtros faltantes) devuelven mensaje `UNSUPPORTED`.
- No integrado al chat ni al Intent Router legacy.
- Montos formateados con separador de miles y dos decimales (sin moneda explícita).

## Evolución futura

1. Plantillas para `LOOKUP_CLIENTE_BY_CUENTA` y `MAX_TRANSACCION_CLIENTE`.
2. Mensajes de error específicos por `metadata.reason` (sin datos, filtro faltante).
3. Integración con `chat.py` para respuestas determinísticas en el asistente.
4. Variantes de tono (ejecutivo, técnico) sobre las mismas plantillas.
5. Internacionalización (es/en) manteniendo lógica determinística.
6. LLM opcional **solo** para parafraseo posterior, nunca para datos.

## Pruebas

Unitarias:

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/test_deterministic_response_engine.py -v --cov=app.response_engine --cov-report=term-missing
```

Integración (pipeline completo + endpoint):

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/integration/test_response_engine_integration.py -v -m integration
```

Cobertura mínima del módulo `app/response_engine`: **90%**.
