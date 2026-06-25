# Guided Fallback Engine v1

## Propósito

El **Guided Fallback Engine** orienta al usuario cuando el pipeline empresarial no puede ejecutar una consulta. No responde con datos ni ejecuta queries: **sugiere**, **recupera contexto** y **guía** antes de delegar a `legacy_chat` como último recurso.

Restricciones v1:

- 100 % determinístico (sin LLM, Ollama ni embeddings)
- 100 % auditable y trazable
- No sustituye al Business Pipeline

## Arquitectura

```
Hybrid Router
│
├─ Conversation Memory (clarificación / follow-up)
│
├─ Semantic Intent + Query Planner
│   ├─ query soportado → Slot Clarification o Business Pipeline
│   └─ UNSUPPORTED → Guided Fallback Engine
│         ├─ respuesta útil → handled_by: guided_fallback
│         └─ None → legacy_chat
```

### Módulo `app/guided_fallback/`

| Componente | Responsabilidad |
|------------|-----------------|
| `types.FallbackType` | Enum de clasificación |
| `schemas.GuidedFallbackResult` | Contrato de salida |
| `classifier` | Clasificación determinística + delegación a legacy |
| `templates` | Textos de orientación por tipo |
| `suggested_questions` | 3–5 preguntas (top queries → capacidades → query types) |
| `engine.GuidedFallbackEngine` | Orquestación `resolve()` |

## Tipos de fallback

| Tipo | Cuándo | Ejemplo |
|------|--------|---------|
| `UNKNOWN` | Descubrimiento de capacidades sin intención parcial | ¿Qué tipos de datos tienes? |
| `AMBIGUOUS` | Pregunta abierta de negocio | ¿Cómo va el negocio? |
| `OUT_OF_DOMAIN` | Tema fuera del dominio empresarial | ¿Quién ganó el mundial? |
| `LOW_CONFIDENCE` | Intención parcial con confianza &lt; 0.45 | Consulta vaga con entidad detectada |
| `UNSUPPORTED_CAPABILITY` | Operación/entidad reconocida pero no ejecutable | Filtros o agregaciones no soportadas |

Si la pregunta es **definicional o conversacional** (`¿Qué es un proveedor?`, `Explícame qué observas…`), el clasificador devuelve `None` y el router delega directamente a `legacy_chat`.

## Integración en Hybrid Router

Punto de enganche: `HybridChatRouter._route_without_memory()` cuando `query_type == UNSUPPORTED`.

**Nota:** Las preguntas de descubrimiento de capacidades (`¿Qué puedes hacer?`, etc.) son interceptadas por **Capability Discovery Engine** antes de llegar a guided fallback. Ver `docs/capability_discovery_v1.md`.

```python
fallback = guided_fallback_engine.resolve(question, intent, query, context)
if fallback is not None:
    return handled_by="guided_fallback"
return legacy_chat(...)
```

`session_id` se propaga en metadata para continuidad conversacional.

## Observabilidad

### Por request (`performance_metrics`)

- `handled_by = guided_fallback`
- `query_type` = `fallback_type` (ej. `UNKNOWN`)
- `success` según `fallback_success`

Metadata en respuesta HTTP:

- `fallback_type`
- `suggested_questions`
- `suggested_questions_count`
- `fallback_success`

### Métricas agregadas

- **GET /api/metrics/summary** — incluye `guided_fallback_requests`
- **GET /api/metrics/routing** — distribución `handled_by`, success rate y top paths (`handled_by` + `query_type`)

## Preguntas sugeridas

Prioridad al generar 3–5 sugerencias:

1. Top queries reales (`performance_metrics`, vía `TopQuestionsProvider` en `deps.py`)
2. Capacidades soportadas (`CAPABILITY_QUESTIONS`)
3. Ejemplos por `BusinessQueryType` (`QUERY_TYPE_EXAMPLE_QUESTIONS`)

## Evolución futura

- Enriquecer patrones de clasificación desde telemetría real
- Personalizar sugerencias por `session_id` / historial
- A/B de plantillas sin cambiar el contrato `GuidedFallbackResult`
- Integrar con un catálogo de capacidades versionado (fuera del router)
- Fallback progresivo: ofrecer clarificación de intención antes de legacy

## Pruebas

- Unitarias: `tests/test_guided_fallback_engine.py`
- Router: `tests/test_hybrid_chat_router.py`
- Integración: `tests/integration/test_hybrid_chat_integration.py`
- Regresión obligatoria: business pipeline, slot clarification, conversation memory intactos
