# Conversational Memory v1

Memoria conversacional determinística, acotada a la sesión actual, para completar clarificaciones de slots y follow-ups cortos sin IA generativa.

## Problema

Tras `slot_clarification`, el usuario respondía con un valor corto (`C001`, `julio`) pero el sistema no podía continuar la consulta porque no existía estado entre turnos.

## Arquitectura

```
Pregunta + session_id
        ↓
ConversationMemoryService.get_or_create(session_id)
        ↓
ContextResolver.resolve(message, context)
        ↓
┌───────────────────────────────────────────────────┐
│ Hit → ejecutar query heredada/completada          │
│       handled_by: conversation_memory             │
├───────────────────────────────────────────────────┤
│ Miss → SemanticIntent → Planner → SlotClarification│
│        → Executor → ResponseEngine                │
│        → actualizar contexto en memoria         │
└───────────────────────────────────────────────────┘
```

Módulo: `app/conversation_memory/`

| Componente | Rol |
|------------|-----|
| `ConversationContext` | Estado mínimo de sesión |
| `ConversationMemoryService` | CRUD en memoria de proceso |
| `ContextResolver` | Clarificaciones + follow-ups |
| `slot_value_parser` | Parseo determinístico de slots |

## ConversationContext

Campos almacenados (sin historial completo ni respuestas):

- `session_id`
- `last_query_type`, `last_operation`, `last_target_entity`
- `last_filters`
- `pending_clarification` (si hay slot pendiente)
- `turn_count`, `created_at`, `updated_at`

## Persistencia v1

```python
dict[str, ConversationContext]  # en memoria del proceso
```

**Limitaciones:**

- Se pierde al reiniciar uvicorn.
- No comparte estado entre workers Gunicorn/Uvicorn múltiples.
- Sin TTL automático en v1.
- El cliente debe enviar el mismo `session_id` en cada turno.

API: `POST /api/chat/hybrid` acepta `session_id` opcional.

## Integración con Slot Clarification

Cuando `handled_by = slot_clarification`, se guarda:

```json
{
  "pending_query_type": "MAX_TRANSACCION_CLIENTE",
  "missing_slots": ["cliente_codigo"],
  "session_token": "...",
  "pending_filters": {}
}
```

## Resolución de clarificaciones

| Turno | Usuario | Sistema |
|-------|---------|---------|
| 1 | ¿Cuál fue la transacción más alta? | `slot_clarification` + guardar pending |
| 2 | C001 | `conversation_memory` → `MAX_TRANSACCION_CLIENTE` + `cliente_codigo=C001` |

## Follow-ups soportados (v1)

| Contexto previo | Mensaje | Resultado |
|-----------------|---------|-----------|
| `COUNT_CLIENTES` | ¿Y proveedores? | `COUNT_PROVEEDORES` |
| `COUNT_PROVEEDORES` | ¿Y clientes? | `COUNT_CLIENTES` |
| `MAX_PROVEEDOR_MES` (mes=N) | ¿Y julio? / ¿Y en julio? | mismo query, `mes=7` |
| `MAX_PROVEEDOR_MES` | ¿Y agosto? | `mes=8` |

Prefijo requerido: mensaje normalizado debe comenzar con `y ` (ej. *¿Y proveedores?*).

## Reglas conservadoras

- Si el mensaje parece **pregunta nueva** (`¿Cuántos clientes existen?`), no se reutiliza `pending_clarification`.
- Si el follow-up no coincide con reglas conocidas → flujo normal (`context_miss`).
- Un solo slot por clarificación en v1.
- Sin embeddings, LLM ni Ollama.

## Observabilidad

Nuevo `handled_by`: **`conversation_memory`**

Metadata por respuesta:

- `context_hit`, `resolution_type`, `clarification_resolved`
- Contadores globales: `context_hits`, `context_misses`, `clarification_resolutions`

Etapa de pipeline: `conversation_memory`.

## Ejemplo multi-turno

```bash
# Turno 1
POST /api/chat/hybrid
{"message": "¿Cuál fue la transacción más alta?", "session_id": "demo-1"}

# Turno 2
POST /api/chat/hybrid
{"message": "C001", "session_id": "demo-1"}
```

## Evolución futura

1. TTL y eviction de sesiones inactivas.
2. Redis/PostgreSQL para multi-worker.
3. Más follow-ups (entidades, años, límites TOP).
4. Validación de `session_token` end-to-end.
5. Integración con `ConceptSet` para follow-ups más robustos.

## Pruebas

```bash
pytest tests/test_conversation_memory.py -q
pytest tests/integration/test_hybrid_chat_integration.py -q
```
