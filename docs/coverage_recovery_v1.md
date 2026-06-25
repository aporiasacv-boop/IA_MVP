# Coverage Recovery v1

Recuperación determinística de preguntas naturales que hoy caen en `guided_fallback` o `legacy_chat`, ampliando sinónimos en catálogos existentes **sin** nuevos query types, LLM ni embeddings.

## Problema

Usuarios empresariales formulan preguntas equivalentes con distinta redacción. Antes de v1, muchas terminaban en fallback aunque el sistema ya soportaba `DATA_COVERAGE`, `DATASET_INFO` o `capability_discovery`.

## Enfoque

| Capa | Cambio |
|------|--------|
| `app/domain/operation_catalog.py` | Sinónimos ampliados para `DATA_COVERAGE` y `DATASET_INFO` |
| `app/capability_discovery/detector.py` | Patrones de discovery refinados; dataset fuera de discovery |
| `app/coverage_recovery/` | Clasificación, métricas, health checks |
| `app/guided_fallback/classifier.py` | Eliminado patrón `que tipos de datos` (ahora resuelve pipeline) |

**No se modificó:** Query Planner, Query Executor, Response Engine, Conversation Memory.

## Consultas equivalentes soportadas

### DATA_COVERAGE → `business_pipeline` / `query_type=DATA_COVERAGE`

| Consulta natural |
|------------------|
| ¿De qué fecha son tus datos? |
| ¿Qué fechas cubren los datos? |
| ¿Hasta qué fecha llegan los datos? |
| ¿Desde cuándo hay información? |
| ¿Cuál es la antigüedad de los datos? |
| ¿Cuál es el rango temporal? |
| ¿Qué periodo de información tienes? |

### DATASET_INFO → `business_pipeline` / `query_type=DATASET_INFO`

| Consulta natural |
|------------------|
| ¿Qué tipos de datos tienes? |
| ¿Qué datos tienes? |
| ¿Qué información tienes? |
| ¿Qué información contiene el sistema? |
| ¿Qué información puedo consultar? |
| ¿Qué datos analiza el asistente? |

### CAPABILITY_DISCOVERY → `handled_by=capability_discovery`

| Consulta natural |
|------------------|
| ¿Qué puedes hacer? |
| ¿Cómo puedes ayudarme? |
| ¿Qué consultas soportas? |
| ¿Qué puedo preguntarte? |
| ¿Qué sabes hacer? |
| ¿Para qué sirves? |

## Desambiguación

- **Dataset vs capability:** `"¿Qué datos tienes?"` → `DATASET_INFO` (volumen/alcance del dataset). `"¿Qué puedes hacer?"` → `capability_discovery` (capacidades del asistente).
- **Prioridad en router:** Capability Discovery se evalúa antes del business pipeline; por eso las frases de dataset se retiraron del detector de discovery.
- **Operation Resolver:** frases multi-palabra más largas tienen prioridad sobre términos cortos como `periodo`.

## Observabilidad

Contadores in-process (patrón `conversation_memory`):

- `coverage_recovery_hits` — pregunta de recuperación enrutada correctamente
- `coverage_recovery_misses` — pregunta de recuperación terminó en `guided_fallback` o `legacy_chat`

Expuestos en:

- Metadata de `POST /api/chat/hybrid`
- `GET /api/metrics/summary`

## Health validation

`validate_coverage_recovery_health()` verifica automáticamente:

1. Ninguna consulta de cobertura termina como `UNSUPPORTED`
2. Ninguna consulta de dataset termina como `UNSUPPORTED` ni es interceptada por discovery
3. Todas las consultas de capability son detectadas por `is_capability_discovery`
4. Consultas empresariales de regresión mantienen su `query_type`

## Pruebas

```bash
pytest tests/test_coverage_recovery.py tests/test_operation_resolver.py \
  tests/test_capability_discovery_engine.py tests/test_system_capabilities_queries.py \
  tests/integration/test_coverage_recovery_integration.py -q
```

## Compatibilidad verificada

Sin cambio de comportamiento para:

- ¿Cuántos clientes existen?
- ¿Cuántos proveedores existen?
- ¿Qué proveedor tuvo más movimiento?
- ¿Cuál fue la transacción más alta?
- Muéstrame los principales clientes
