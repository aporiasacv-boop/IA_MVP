# Capability Discovery Engine v1

## Propósito

El **Capability Discovery Engine** transforma preguntas de descubrimiento en una experiencia guiada basada en las capacidades **reales** del asistente. No ejecuta consultas empresariales ni usa IA generativa: describe dominios, consultas soportadas y ejemplos ejecutables.

## Arquitectura

```
Hybrid Router
│
├─ Conversation Memory
├─ Semantic Intent + Planner
├─ Capability Discovery   ← preguntas de descubrimiento
├─ Business Pipeline / Slot Clarification
├─ Guided Fallback
└─ Legacy Chat
```

`Capability Discovery` se evalúa **antes** del business pipeline cuando la pregunta coincide con patrones de descubrimiento, y **antes** de `guided_fallback` en el flujo de consultas no ejecutables.

### Módulo `app/capability_discovery/`

| Componente | Responsabilidad |
|------------|-----------------|
| `detector` | Identifica preguntas de descubrimiento |
| `registry` | Capacidades desde `BusinessQueryType` y `SYSTEM_CAPABILITY_KEYS` |
| `example_questions` | 5–10 ejemplos (top queries → query types → capacidades) |
| `engine` | Orquestación `discover()` |
| `health` | Validación automática del catálogo expuesto |

## Capacidades

### Cobertura de datos

Derivada de `SYSTEM_CAPABILITY_KEYS` en `system_repository.py` y etiquetas en `response_templates.py`:

- Clientes, Proveedores, Cuentas, KPIs, Rankings, Actividad mensual, Insights empresariales

### Consultas empresariales

Derivadas de `BusinessQueryType` ejecutables en `BusinessQueryExecutor` (excluye `UNSUPPORTED` y `SYSTEM_CAPABILITIES`).

## Generación de ejemplos

Prioridad al construir 5–10 preguntas:

1. Top queries reales (`performance_metrics`)
2. Ejemplos por `BusinessQueryType` (`QUERY_TYPE_EXAMPLE_QUESTIONS`)
3. Capacidades principales (`PRIMARY_CAPABILITY_QUESTIONS`)

Incluye ejemplos como:

- ¿Cuántos clientes existen?
- ¿Quién es el principal proveedor?
- ¿Qué proveedor tuvo más movimiento en junio?
- ¿Cuál es el periodo de los datos?

## Integración

`handled_by = capability_discovery`

Preguntas detectadas (entre otras):

- ¿Qué puedes hacer?
- ¿Qué información manejas?
- ¿Qué datos tienes?
- ¿Qué puedo preguntarte?
- ¿Qué consultas soportas?

**No** intercepta `¿Qué tipos de datos tienes?` — esa pregunta sigue en `guided_fallback` (UNKNOWN).

## Observabilidad

Por request:

- `handled_by = capability_discovery`
- `query_type = capability_discovery`
- `capabilities_count`, `example_questions_count`, `discovery_success`

Métricas agregadas:

- `capability_discovery_requests` en **GET /api/metrics/summary**
- Distribución en **GET /api/metrics/routing**

## Health Validation

`tests/test_capability_discovery_health.py` valida:

1. Al menos una capacidad registrada
2. Al menos una pregunta ejemplo
3. Ninguna pregunta ejemplo vacía
4. Capacidades alineadas con `BusinessQueryType` y catálogo del sistema
5. Cada ejemplo mapea a un query type soportado vía planner

## Limitaciones

- No consulta el Data Mart en tiempo real (cobertura desde catálogo registrado)
- No personaliza por sesión ni historial
- Patrones de detección basados en texto normalizado (sin embeddings)
- `MAX_TRANSACCION_CLIENTE` puede requerir clarificación de slots al ejecutarse

## Evolución futura

- Enriquecer ejemplos desde telemetría con validación automática
- Exponer cobertura temporal real opcional (sin ejecutar query completa del usuario)
- Catálogo versionado compartido con documentación ejecutiva
- Sugerencias contextuales post-discovery en conversational memory

## Pruebas

- Unitarias: `tests/test_capability_discovery_engine.py`
- Health: `tests/test_capability_discovery_health.py`
- Router: `tests/test_hybrid_chat_router.py`
- Integración: `tests/integration/test_hybrid_chat_integration.py`
