# Capability Discovery v2

Evolución UX del componente **Capability Discovery** sin cambiar arquitectura, Query Planner, Executor, Memory ni Guided Fallback.

## Problema (v1)

La respuesta anterior parecía una **página de ayuda**:

- Demasiadas capacidades (rankings, cuentas, cobertura técnica)
- 5–10 ejemplos mezclados con preguntas conversacionales
- Secciones técnicas (`Cobertura de datos`, `Consultas soportadas`)
- Bloque adicional `También puedes consultar` (Suggested Questions)

## Objetivos UX

1. **Conversación breve**, no catálogo de funcionalidades
2. **Lenguaje de negocio**, sin terminología de implementación
3. **Menos ruido visual** — máximo 5 dominios y 3 ejemplos
4. **Sin sugerencias redundantes** tras la respuesta de discovery

## Diseño conversacional

### Plantilla v2 (≤ 12 líneas)

```
Puedo ayudarte con información sobre:

• Clientes
• Proveedores
• KPIs
• Actividad mensual
• Insights empresariales

Por ejemplo:
• ¿Cuántos clientes existen?
• ¿Quién es el principal cliente?
• ¿Qué proveedor tuvo más movimiento en junio?
```

### Reglas de visualización

| Regla | Valor |
|-------|-------|
| Capacidades visibles | Máx. 5 (lista fija de negocio) |
| Ejemplos | Máx. 3 (lista fija ejecutable) |
| Líneas totales | Máx. 12 |
| Suggested Questions | **No** cuando `handled_by = capability_discovery` |
| Secciones extra | Prohibidas |

### Eliminado de la respuesta visible

- Rankings, Cuentas, Cobertura de datos
- Query Types, dataset, capacidades soportadas
- Ejemplos conversacionales: Hola, ¿Quién eres?, ¿Qué es un proveedor?, ¿Qué sabes hacer?

## Implementación

| Módulo | Rol |
|--------|-----|
| `app/capability_discovery/v2/constants.py` | Listas fijas y términos prohibidos |
| `app/capability_discovery/v2/formatter.py` | Construye la respuesta |
| `app/capability_discovery/v2/validation.py` | Valida límites UX |
| `app/capability_discovery/v2/metrics.py` | Observabilidad v2 |
| `app/capability_discovery/engine.py` | Orquesta discover() v2 |
| `hybrid_chat_router._attach_suggestions` | Omite sugerencias en discovery |

## Observabilidad

- `capability_discovery_v2_responses` — contador de respuestas v2
- `capability_discovery_response_length` — líneas de la última respuesta

Disponibles en metadata de `/api/chat/hybrid` y `GET /api/metrics/summary`.

## Reducción de ruido

| Antes (v1) | Después (v2) |
|------------|--------------|
| 7+ capacidades técnicas | 5 dominios de negocio |
| 5–10 ejemplos dinámicos | 3 ejemplos curados |
| 4 secciones | 2 bloques (intro + ejemplos) |
| Suggested Questions activas | Sin bloque "También puedes consultar" |

## Pruebas

```bash
pytest tests/test_capability_discovery_engine.py \
  tests/test_capability_discovery_health.py \
  tests/integration/test_capability_discovery_v2_integration.py -q
```

## Restricciones respetadas

- Sin nuevas capacidades de negocio
- Sin nuevos dominios ni query types
- Sin cambios en planner, executor, memory ni guided fallback
- Registry v1 (`registry.py`) se conserva para otros consumidores internos
