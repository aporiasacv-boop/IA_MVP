# Business Semantic Intent Builder

## Objetivo

Componente central del futuro **Semantic Router Empresarial** del Asistente de Inteligencia Empresarial Olnatura.

Unifica las salidas de **Operation Resolver** y **Entity Resolver** en un contrato canónico tipado (`BusinessSemanticIntent`) listo para ser consumido por el **Business Query Engine**, sin utilizar Ollama, LLMs, embeddings ni bases vectoriales.

Este sprint es **aditivo**: no modifica el Intent Router, el chat, la Executive Summary Layer ni los resolvers existentes.

## Arquitectura

```
Pregunta (texto)
      │
      ▼
SemanticIntentBuilder
      │
      ├─ OperationResolver.resolve()
      │       └─ operation, operation_confidence
      │
      ├─ EntityResolver.resolve()
      │       └─ entities, parameters, entity_confidence
      │
      ├─ Reconciliación de operación (v1)
      │
      ├─ TargetEntityResolver.resolve()
      │       └─ target_entity, source_entity
      │
      ├─ Construcción de BusinessFilters
      │
      └─ confidence = (operation_confidence + entity_confidence) / 2
      │
      ▼
BusinessSemanticIntent
```

### Componentes

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Schema | `app/schemas/semantic_intent.py` | Contratos `BusinessFilters` y `BusinessSemanticIntent` |
| Servicio | `app/services/semantic_intent_builder.py` | Orquestación de resolvers y ensamblaje del intent |
| Servicio | `app/services/target_entity_resolver.py` | Reglas v1 de target/source entity |
| API | `app/api/routes/semantic.py` | Endpoint de prueba `/api/semantic/intent` |

## Flujo completo

1. **Resolución de operación** — `OperationResolver` detecta la operación analítica (`COUNT`, `MAX`, `LOOKUP`, etc.).
2. **Resolución de entidades** — `EntityResolver` detecta entidades y parámetros (`mes`, `anio`, `codigo`).
3. **Reconciliación de operación (v1)** — Corrige ambigüedades conocidas sin modificar los resolvers.
4. **Resolución de target/source** — `TargetEntityResolver` aplica reglas v1 sobre operación + entidades.
5. **Construcción de filtros** — Los parámetros del `EntityResolver` se mapean a `BusinessFilters`.
6. **Cálculo de confidence** — Promedio simple entre ambos resolvers.
7. **Ensamblaje** — Se devuelve `BusinessSemanticIntent` con la pregunta original trazable.

## TargetEntityResolver (reglas v1)

Reglas evaluadas en orden. La primera que aplica determina el resultado.

| # | Condición | target_entity | source_entity |
|---|-----------|---------------|---------------|
| 1 | `COUNT` + `CLIENTE` | `CLIENTE` | `None` |
| 2 | `COUNT` + `PROVEEDOR` | `PROVEEDOR` | `None` |
| 3 | `MAX` + `TRANSACCION` | `TRANSACCION` | `CLIENTE` si existe |
| 4 | `MAX` + `PROVEEDOR` | `PROVEEDOR` | `None` |
| 5 | `LOOKUP` + `CLIENTE` + `CUENTA` | `CLIENTE` | `CUENTA` |
| 6 | `LOOKUP` + `PROVEEDOR` + `CUENTA` | `PROVEEDOR` | `CUENTA` |
| 7 | Fallback | Primera entidad detectada | `None` |

## Reconciliación de operación (reglas v1)

Capa adicional en `SemanticIntentBuilder` que no modifica los resolvers existentes. Se aplica después de consultarlos.

| # | Condición | Operación resultante |
|---|-----------|---------------------|
| R1 | `CLIENTE` + `CUENTA` + `codigo` | `LOOKUP` (prioridad sobre `COUNT` ambiguo) |
| R2 | `TRANSACCION` + `CLIENTE` y operación nula | `MAX` |
| R3 | `PROVEEDOR` + `MOVIMIENTO` y operación nula | `MAX` |
| R4 | En cualquier otro caso | Operación del `OperationResolver` |

## SourceEntityResolver implícito

No existe un componente separado en esta versión. La resolución de `source_entity` está embebida en `TargetEntityResolver`:

- **Regla 3** — `CLIENTE` como origen cuando se busca la transacción máxima de un cliente.
- **Reglas 5 y 6** — `CUENTA` como origen en consultas de pertenencia (`LOOKUP`).
- **Resto de reglas** — `source_entity = None`.

Un `SourceEntityResolver` independiente podrá extraerse en versiones futuras si las reglas crecen en complejidad.

## Contrato BusinessSemanticIntent

```json
{
  "operation": "MAX",
  "target_entity": "TRANSACCION",
  "source_entity": "CLIENTE",
  "filters": {
    "cliente_codigo": "C001",
    "proveedor_codigo": null,
    "cuenta_codigo": null,
    "mes": null,
    "anio": null
  },
  "confidence": 0.95,
  "source_question": "¿Cuál fue la transacción más alta del cliente C001?"
}
```

### BusinessFilters

| Campo | Origen | Ejemplo |
|-------|--------|---------|
| `cliente_codigo` | `CLIENTE` + `codigo` | `C001` |
| `proveedor_codigo` | `PROVEEDOR` + `codigo` | `P0001` |
| `cuenta_codigo` | `CUENTA` + `codigo` | `IMA0709183` |
| `mes` | Nombre de mes → entero (1–12) | `junio` → `6` |
| `anio` | Año numérico del `EntityResolver` | `2025` |

Prioridad de asignación de código: `CUENTA` > `CLIENTE` > `PROVEEDOR`.

## Endpoint de prueba

```
GET /api/semantic/intent?question=¿Cuál fue la transacción más alta del cliente C001?
```

## Casos de uso

| Pregunta | operation | target | source | Filtros |
|----------|-----------|--------|--------|---------|
| ¿Cuántos clientes existen? | `COUNT` | `CLIENTE` | — | — |
| ¿Qué proveedor tuvo más movimiento en junio? | `MAX` | `PROVEEDOR` | — | `mes=6` |
| ¿Cuál fue la transacción más alta del cliente C001? | `MAX` | `TRANSACCION` | `CLIENTE` | `cliente_codigo=C001` |
| ¿De qué cliente es la cuenta IMA0709183? | `LOOKUP` | `CLIENTE` | `CUENTA` | `cuenta_codigo=IMA0709183` |
| ¿Cuál fue la actividad de proveedores en 2025? | — | `PROVEEDOR` | — | `anio=2025` |

## Limitaciones actuales

- Depende de la cobertura de los catálogos de `OperationResolver` y `EntityResolver`; si no detectan operación o entidad, el intent queda incompleto.
- Las reglas de `TargetEntityResolver` son v1 y cubren solo combinaciones frecuentes del MVP.
- No resuelve contexto conversacional ni referencias pronominales.
- No genera SQL ni consulta PostgreSQL.
- `confidence` es un promedio simple, no una probabilidad calibrada.
- No está integrado al chat ni al Intent Router existente.

## Evolución futura hacia Business Query Engine

1. **Semantic Router unificado** — Pipeline completo: lenguaje humano → intent semántico.
2. **Business Query Engine** — Traducir `BusinessSemanticIntent` a consultas SQL/ORM parametrizadas.
3. **SourceEntityResolver** — Extraer reglas de origen a componente dedicado.
4. **Enriquecimiento de reglas** — Más combinaciones operación × entidad (`SUM` + `MOVIMIENTO`, `TREND` + `ANIO`, etc.).
5. **Context Resolver** — Resolver filtros implícitos y referencias a turnos anteriores.
6. **Telemetría** — Medir cobertura de reglas y confianza en producción.

## Pruebas

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/test_semantic_intent_builder.py -v
```

Cobertura mínima del sprint: **5 casos obligatorios** + endpoint + caso sin coincidencias.
