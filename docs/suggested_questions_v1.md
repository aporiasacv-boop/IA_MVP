# Suggested Questions Engine v1

## Propósito

El **Suggested Questions Engine** fomenta la exploración conversacional después de cada respuesta del Hybrid Router. No ejecuta consultas ni modifica el contenido principal de la respuesta: añade un bloque de **próximos pasos** determinísticos.

## Arquitectura

```
HybridChatRouter.route()
  → handler (business_pipeline | slot_clarification | ...)
  → SuggestedQuestionsEngine.generate()
  → HybridChatResult.suggestions
```

### Módulo `app/suggested_questions/`

| Componente | Responsabilidad |
|------------|-----------------|
| `schemas.SuggestedQuestionsResult` | Contrato de salida |
| `rules` | Reglas por `BusinessQueryType` y contexto |
| `engine` | Orquestación y priorización |
| `validator` | Filtra sugerencias no soportadas por el planner |
| `health` | Validación automática del catálogo |

Catálogo compartido en `app/query_engine/query_catalog.py`.

## Generación

Método:

```python
engine.generate(
    current_query_type=...,
    current_operation=...,
    current_entity=...,
    conversation_context=...,
    handled_by=...,
)
```

### Prioridades

1. Reglas por tipo de consulta actual (`TYPE_SPECIFIC_RULES`)
2. Top queries reales (`performance_metrics`)
3. Query types relacionados (`RELATED_QUERY_TYPES`)
4. Capacidades soportadas (`QUERY_TYPE_EXAMPLE_QUESTIONS`)
5. Preguntas de discovery (`DISCOVERY_QUESTIONS`)

### Reglas iniciales

| Query Type | Sugerencias orientativas |
|------------|-------------------------|
| `COUNT_CLIENTES` | Principal cliente, proveedores, periodo |
| `TOP_CLIENTES` | Proveedores, movimiento mensual, clientes |
| `MAX_PROVEEDOR_MES` | Otro mes, rankings, clientes activos |

Las preguntas se validan con `BusinessQueryPlanner`: solo se exponen sugerencias que mapean a query types implementados.

### Límites

- Mínimo: 3 preguntas
- Máximo: 5 preguntas
- Siempre únicas

## Integración

### Schemas extendidos

- `BusinessResponse.suggestions`
- `CapabilityDiscoveryResult.suggestions`
- `GuidedFallbackResult.suggestions`
- `HybridChatResult.suggestions` (API principal)

El campo `answer` **no se modifica**. Las sugerencias viajan en `suggestions.questions` y en metadata:

- `suggested_questions`
- `suggested_questions_count`
- `suggested_questions_source`
- `suggested_questions_generated`
- `suggested_questions_clicked` (placeholder `0`)

## Observabilidad

Por request en `performance_metrics`:

- `suggested_questions_count`

Agregados en **GET /api/metrics/summary**:

- `suggested_questions_generated`
- `average_suggestions_per_response`

Migración: `006_add_suggested_questions_metrics`.

## Frontend

Componente `SuggestedQuestionsFollowUp`:

```
También puedes consultar:
• pregunta 1
• pregunta 2
```

Los clics reutilizan `submitQuestion` — no se ejecutan automáticamente.

## Health Validation

`tests/test_suggested_questions_health.py` valida:

1. Sugerencias únicas
2. Texto no vacío
3. Correspondencia con capacidades reales
4. Compatibilidad con el planner (sin excepciones)

## Evolución futura

- Personalización por `session_id` / historial
- Tracking real de `suggested_questions_clicked`
- Reglas dinámicas desde telemetría
- Sugerencias post–slot clarification contextualizadas

## Pruebas

- Unitarias: `tests/test_suggested_questions_engine.py`
- Health: `tests/test_suggested_questions_health.py`
- Integración: `tests/integration/test_hybrid_chat_integration.py`
