# AI Orchestration Layer v1

## Objetivo

Conectar cualquier modelo LLM al stack empresarial **sin modificar** ETL, Data Mart, Planner, Executor, EKO, ERO, SBEP ni EEP. El LLM consume exclusivamente el **Enterprise Evidence Package**.

## Arquitectura

```
Pregunta
    ↓
Evidence Package Service (EEP)
    ↓
Prompt Builder (solo EEP)
    ↓
Hallucination Guard
    ↓
BaseLLMProvider (config)
    ↓
Executive Response Engine
    ↓
Respuesta ejecutiva estructurada
```

Integración mínima con Hybrid Router cuando `handled_by = executive_reasoning` (verbos ejecutivos + query no soportada por pipeline determinístico).

## Proveedores

| Proveedor | Configuración |
|-----------|---------------|
| `mock` | `LLM_PROVIDER=mock` (default, pruebas) |
| `openai` | `LLM_PROVIDER=openai`, `OPENAI_API_KEY`, `OPENAI_MODEL` |
| `claude` | `LLM_PROVIDER=claude`, `ANTHROPIC_API_KEY`, `CLAUDE_MODEL` |
| `ollama` | `LLM_PROVIDER=ollama`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL` |

Fallback opcional: `LLM_FALLBACK_PROVIDER`

La selección es **100% por configuración** — nunca hardcodeada en lógica de negocio.

## Prompt Builder

Construye texto legible desde EEP:
- Pregunta, contexto empresarial, hallazgos, riesgos, oportunidades, recomendaciones, limitaciones, confianza
- **Excluye:** SQL, JSON interno, metadatos técnicos (`package_id`, `schema_version`, etc.)

## Executive Response

```json
{
  "executive_summary": "...",
  "detailed_analysis": "...",
  "confidence": 0.89,
  "citations": [{"key": "...", "source": "eko"}],
  "limitations": ["..."],
  "provider": "mock",
  "model": "mock-executive-v1",
  "tokens_input": 500,
  "tokens_output": 200,
  "estimated_cost": 0.0,
  "response_time": 0.12
}
```

## API

```
POST /api/executive-response/generate
POST /api/executive-response/generate-from-package
GET  /api/executive-response/schema
GET  /api/executive-response/statistics
GET  /api/executive-response/health
GET  /api/ai-costs/summary
```

## Anti-alucinación

1. **Pre-LLM:** validación de evidencia suficiente en EEP
2. **Limitaciones críticas:** bloqueo si falta EKO/entidad
3. **Post-LLM:** respuesta vacía o sin citas → guard activado
4. **Prompt:** instrucciones explícitas de no inventar datos

## Costos

Variables en `settings.py`:
- `GPT_COST_PER_1K_INPUT_TOKENS` / `OUTPUT`
- `CLAUDE_COST_PER_1K_INPUT_TOKENS` / `OUTPUT`
- `OLLAMA_COST_PER_1K_TOKENS`
- `ESTIMATED_TOKENS_PER_EXECUTIVE_CALL`

Métricas: `llm_requests`, `provider_distribution`, `tokens_input/output`, `estimated_cost`, `average_latency`, `hallucination_guard_triggered`, `llm_fallbacks`

## Extensibilidad

1. Implementar `BaseLLMProvider`
2. Registrar en `providers/factory.py`
3. Añadir variables de costo en settings
4. Sin cambios en EEP ni capas anteriores

## UI

Ruta `/costos-ia` — costos por proveedor, diario, mensual, por consulta, tokens y latencia.
