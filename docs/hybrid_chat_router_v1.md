# Hybrid Chat Router v1

## Objetivo

Integrar de forma **aditiva** el pipeline empresarial determinístico con el chat legacy (Intent Router + DeterministicResponseEngine legacy + Ollama) mediante un router híbrido que selecciona automáticamente el camino correcto.

El usuario hace una pregunta; el sistema decide si responde con datos verificados del Data Mart o delega al flujo conversacional existente.

## Arquitectura híbrida

```
                    Pregunta
                        │
                        ▼
               HybridChatRouter
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
  query_type != UNSUPPORTED      query_type == UNSUPPORTED
         │                             │
         ▼                             ▼
  Business Pipeline              Legacy Chat
         │                             │
  Intent Builder                     Human Language Layer
  Query Planner                      Intent Router
  Query Executor                     Deterministic Engine legacy
  Response Engine v1                 Ollama (si aplica)
         │                             │
         └──────────────┬──────────────┘
                        ▼
                 HybridChatResult
```

### Componentes

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Schema | `app/schemas/hybrid_chat.py` | `HybridChatRequest`, `HybridChatResult` |
| Router | `app/services/hybrid_chat_router.py` | Decisión y orquestación |
| API | `app/api/routes/hybrid_chat.py` | `POST /api/chat/hybrid` |
| DI | `app/api/deps.py` | `get_hybrid_chat_router` |

## Flujo de decisión

1. `SemanticIntentBuilder.build(message)` produce el intent semántico.
2. `BusinessQueryPlanner.plan(intent)` produce `BusinessQuery`.
3. Si `query_type != UNSUPPORTED`:
   - Ejecutar `BusinessQueryExecutor` + `DeterministicResponseEngine` v1.
   - `handled_by = "business_pipeline"`.
4. Si `query_type == UNSUPPORTED`:
   - Delegar al handler del chat legacy (`/api/chat` internamente).
   - `handled_by = "legacy_chat"`.

## Fallback

El fallback al chat legacy ocurre cuando el planner no puede mapear la pregunta a un `BusinessQueryType` soportado:

- Preguntas conceptuales (`¿Qué es un proveedor?`)
- Preguntas abiertas (`Explícame qué observas en estos datos`)
- Consultas aún no modeladas en el pipeline empresarial

El chat legacy **no se modifica**; se invoca el mismo handler con las mismas dependencias.

## Endpoint experimental

```
POST /api/chat/hybrid
```

Request:

```json
{
  "message": "¿Cuántos clientes existen?"
}
```

Response:

```json
{
  "handled_by": "business_pipeline",
  "success": true,
  "answer": "Actualmente existen 50 clientes registrados.",
  "metadata": {
    "handled_by": "business_pipeline",
    "query_type": "COUNT_CLIENTES",
    "confidence": 1.0
  }
}
```

## Casos soportados (business pipeline)

| Pregunta ejemplo | `query_type` | `handled_by` |
|------------------|--------------|--------------|
| ¿Cuántos clientes existen? | `COUNT_CLIENTES` | `business_pipeline` |
| ¿Cuántos proveedores existen? | `COUNT_PROVEEDORES` | `business_pipeline` |
| Muéstrame los principales clientes | `TOP_CLIENTES` | `business_pipeline` |
| ¿Qué proveedor tuvo más movimiento en junio? | `MAX_PROVEEDOR_MES` | `business_pipeline` |

## Casos no soportados (legacy chat)

| Pregunta ejemplo | `handled_by` |
|------------------|--------------|
| ¿Qué es un proveedor? | `legacy_chat` |
| Explícame qué observas en estos datos | `legacy_chat` |
| Hola, buenos días | `legacy_chat` |

## Trazabilidad

`metadata` incluye como mínimo:

**Pipeline empresarial:**

```json
{
  "handled_by": "business_pipeline",
  "query_type": "COUNT_CLIENTES",
  "confidence": 0.95
}
```

**Legacy chat:**

```json
{
  "handled_by": "legacy_chat",
  "intent": "UNKNOWN",
  "confidence": 0.4,
  "response_mode": "GENERATIVE"
}
```

## Restricciones

- No reemplaza `POST /api/chat`.
- No elimina Intent Router, Ollama ni DeterministicResponseEngine legacy.
- No introduce LLM en el pipeline empresarial.
- No integra Narrative Layer.

## Evolución futura

1. Promover `/api/chat/hybrid` a `/api/chat` con feature flag.
2. Telemetría de ratio `business_pipeline` vs `legacy_chat`.
3. Enriquecer planner para reducir fallback.
4. Unificar metadata en el frontend del asistente.
5. Respuestas híbridas: pipeline + explicación LLM solo sobre datos verificados.

## Pruebas

Unitarias:

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/test_hybrid_chat_router.py -v --cov=app.services.hybrid_chat_router --cov-report=term-missing
```

Integración:

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/integration/test_hybrid_chat_integration.py -v -m integration
```
