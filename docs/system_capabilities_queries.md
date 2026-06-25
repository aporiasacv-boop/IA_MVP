# Consultas de capacidades, cobertura y dataset

Este documento describe el soporte determinístico para preguntas sobre el sistema, la cobertura temporal y el volumen del dataset en el pipeline empresarial de Olnatura.

## Propósito

Durante pruebas reales se identificaron preguntas frecuentes que caían en `UNSUPPORTED` y terminaban en `legacy_chat` con respuestas genéricas:

- ¿Qué datos tienes?
- ¿Cuántos datos tienes?
- ¿Qué puedo preguntarte?
- ¿Cuál es el periodo de los datos?
- ¿Qué fechas cubren los datos?

El objetivo es responder de forma **100% determinística**, **auditable** y **trazable**, sin IA generativa ni nuevas capas arquitectónicas.

## Operaciones nuevas (`BusinessOperation`)

| Operación | Descripción |
|-----------|-------------|
| `SYSTEM_INFO` | Capacidades y alcance del asistente |
| `DATA_COVERAGE` | Rango temporal del dataset |
| `DATASET_INFO` | Volumen agregado (movimientos, clientes, proveedores) |

Sinónimos definidos en `app/domain/operation_catalog.py` y resueltos por `OperationResolver`.

## Query types (`BusinessQueryType`)

| Operación | Query Type |
|-----------|------------|
| `SYSTEM_INFO` | `SYSTEM_CAPABILITIES` |
| `DATA_COVERAGE` | `DATA_COVERAGE` |
| `DATASET_INFO` | `DATASET_INFO` |

Mapeo en `app/query_engine/query_planner.py`.

## Flujo en el pipeline

```
Pregunta
  ↓ OperationResolver  → SYSTEM_INFO | DATA_COVERAGE | DATASET_INFO
  ↓ BusinessQueryPlanner → SYSTEM_CAPABILITIES | DATA_COVERAGE | DATASET_INFO
  ↓ SystemRepository   → datos del Data Mart o catálogo estático
  ↓ Response Engine    → respuesta ejecutiva en español
```

## Fuentes de datos

`app/repositories/query_executor/system_repository.py`:

| Método | Fuente | Notas |
|--------|--------|-------|
| `get_dataset_info()` | `mv_resumen_mensual`, `fact_cliente`, `fact_proveedor` | No consulta `movimientos_diario`; usa agregados existentes |
| `get_data_coverage()` | `mv_resumen_mensual` | `fecha_min` / `fecha_max` derivados del periodo mensual |
| `get_system_capabilities()` | Catálogo estático | Sin SQL; lista auditable de dominios soportados |

Capacidades estructuradas: `clientes`, `proveedores`, `cuentas`, `kpis`, `top_clientes`, `top_proveedores`, `actividad_mensual`, `insights`.

## Ejemplos de respuesta

### SYSTEM_CAPABILITIES

> Actualmente puedo consultar información relacionada con:
>
> • Clientes  
> • Proveedores  
> • Cuentas  
> • KPIs  
> • Rankings  
> • Actividad mensual  
> • Insights empresariales

### DATA_COVERAGE

> Los datos disponibles abarcan desde el 2025-01-01 hasta el 2025-12-31.

### DATASET_INFO

> Actualmente analizo:
>
> • 386,480 movimientos  
> • 50 clientes  
> • 766 proveedores

## Observabilidad

Las preguntas cubiertas por este módulo **no** deben enrutarse a `legacy_chat`. En `POST /api/chat/hybrid` se registran con:

- `handled_by = business_pipeline`
- `query_type` ∈ `{ SYSTEM_CAPABILITIES, DATA_COVERAGE, DATASET_INFO }`

## Rollback y compatibilidad

- No se modificó el Hybrid Router ni el chat legacy.
- Preguntas no cubiertas siguen resolviendo a `UNSUPPORTED` → `legacy_chat`.
- El frontend no requiere cambios: consume la misma respuesta `answer` del pipeline híbrido.

## Evolución futura

1. **Enriquecer `DATASET_INFO`** con conteo de cuentas desde `fact_cuenta` si el negocio lo solicita.
2. **Capacidades dinámicas** derivadas de feature flags o permisos por rol (manteniendo determinismo).
3. **Sinónimos adicionales** en `operation_catalog.py` según telemetría de `top-queries`.
4. **Desambiguación** entre `SYSTEM_INFO` y `DATASET_INFO` cuando coexisten términos como “datos” (prioridad por frases multi-palabra en el resolver).

## Pruebas

```bash
pytest tests/test_system_capabilities_queries.py tests/test_query_planner.py tests/test_business_query_executor.py tests/test_deterministic_response_engine.py -q
```

Casos obligatorios cubiertos en `test_system_capabilities_queries.py` y `test_query_planner.py`.
