# Slot Clarification Engine v1

Motor determinístico que detecta filtros obligatorios faltantes en consultas empresariales ya entendidas y solicita **un único dato** antes de ejecutar el pipeline.

## Problema que resuelve

Consultas con intención clara pero parámetro incompleto terminaban en:

- `UNSUPPORTED`
- `legacy_chat`
- respuestas genéricas de fallback

Ejemplos:

| Pregunta | Query type | Slot faltante |
|----------|------------|---------------|
| ¿Cuál fue la transacción más alta? | `MAX_TRANSACCION_CLIENTE` | `cliente_codigo` |
| ¿Qué proveedor tuvo más movimiento? | `MAX_PROVEEDOR_MES` | `mes` |
| ¿De qué cliente es la cuenta? | `LOOKUP_CLIENTE_BY_CUENTA` | `cuenta_codigo` |

## Arquitectura

```
Pregunta
  ↓
SemanticIntentBuilder
  ↓
BusinessQueryPlanner
  ↓
SlotClarificationEngine.resolve()
  ↓
┌─────────────────────────────────────┐
│ Faltan slots → slot_clarification   │  (NO executor, NO response engine)
│ Slots completos → business_pipeline │
└─────────────────────────────────────┘
```

Módulo: `app/slot_clarification/`

| Archivo | Responsabilidad |
|---------|-----------------|
| `slots.py` | Enum `ClarificationSlot` |
| `schemas.py` | `SlotClarificationResult` |
| `templates.py` | Mensajes determinísticos por slot |
| `required_slots.py` | Mapeo query type → slots obligatorios |
| `engine.py` | `SlotClarificationEngine` |

## Slots soportados (v1)

| Slot | Filtro | Plantilla |
|------|--------|-----------|
| `CLIENTE_CODIGO` | `cliente_codigo` | ¿De qué cliente deseas consultar la información? |
| `MES` | `mes` | ¿De qué mes deseas realizar la consulta? |
| `CUENTA_CODIGO` | `cuenta_codigo` | ¿Cuál es el código de cuenta? |
| `PROVEEDOR_CODIGO` | `proveedor_codigo` | Reservado para evolución |
| `ANIO` | `anio` | Reservado para evolución |

## Query types con slots obligatorios

```python
MAX_TRANSACCION_CLIENTE → cliente_codigo
MAX_PROVEEDOR_MES       → mes
LOOKUP_CLIENTE_BY_CUENTA → cuenta_codigo
```

## Contrato de respuesta

`SlotClarificationResult`:

- `success`: siempre `True` en v1 (la clarificación es una respuesta válida)
- `answer`: pregunta al usuario
- `pending_query_type`: consulta pendiente de ejecutar
- `missing_slots`: lista ordenada de slots faltantes
- `session_token`: UUID para correlación futura (sin persistencia en v1)
- `metadata`: trazabilidad (`clarification_type`, `confidence`, `source_question`)

En `POST /api/chat/hybrid`:

```json
{
  "handled_by": "slot_clarification",
  "success": true,
  "answer": "¿De qué cliente deseas consultar la información?",
  "metadata": {
    "pending_query_type": "MAX_TRANSACCION_CLIENTE",
    "missing_slots": ["cliente_codigo"],
    "session_token": "..."
  }
}
```

## Observabilidad

Nuevo `handled_by`: **`slot_clarification`**

Se registra en `performance_metrics`:

- `pending_query_type` como `query_type`
- `missing_slots` en metadata de respuesta
- Etapa `slot_clarification` en tiempos de pipeline

## Integración

`HybridChatRouter` invoca el engine **después del planner** y **antes del executor**:

1. Si `query_type != UNSUPPORTED` y hay slots faltantes → clarificación
2. Si no hay slots faltantes → flujo normal (`business_pipeline`)
3. **No** se llama a `BusinessQueryExecutor` ni `DeterministicResponseEngine` durante clarificación

## Limitaciones v1

- **Sin memoria conversacional**: `session_token` se genera pero no se persiste ni rehidrata contexto.
- **Un slot por turno**: se pregunta solo el primero de `missing_slots`.
- **Sin Ollama / LLM / embeddings**: 100% determinístico.
- El planner debe emitir el `query_type` aunque falten filtros (cambio coordinado en `BusinessQueryPlanner`).

## Evolución futura

1. **Conversational Memory v1**: persistir `pending_query_type`, filtros parciales y `session_token`.
2. **Resolución de follow-up**: usuario responde `"C001"` → merge de slot y ejecución automática.
3. **Más query types**: slots para `anio`, `proveedor_codigo`, rangos de fechas.
4. **Integración con ConceptSet**: priorizar slot más probable según conceptos detectados.

## Pruebas

```bash
pytest tests/test_slot_clarification_engine.py tests/test_hybrid_chat_router.py -q
pytest tests/integration/test_hybrid_chat_integration.py::test_integration_hybrid_slot_clarification_max_transaccion -q
```
