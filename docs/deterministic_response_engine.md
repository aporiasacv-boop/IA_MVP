# Deterministic Response Engine

## Objetivo

Responder consultas empresariales frecuentes sin invocar Ollama, Prompt Builder ni Response Generator, utilizando datos ya materializados en la capa ejecutiva, KPIs e Insights.

## Arquitectura

```
Pregunta
  → HumanLanguageLayer
  → EntityExtractionLayer
  → Capas conversacionales (token / system / social)
  → IntentRouter
  → ResponseModeResolver
        ├─ DETERMINISTIC → DeterministicResponseEngine
        └─ GENERATIVE    → QueryExecutor / BusinessContextBuilder → ResponseGenerator (Ollama)
```

### Componentes

| Componente | Ruta | Rol |
|------------|------|-----|
| ResponseMode | `app/schemas/response_mode.py` | Enum `DETERMINISTIC` / `GENERATIVE` |
| ResponseModeResolver | `app/services/response_mode_resolver.py` | Clasifica intención → modo |
| DeterministicResponseEngine | `app/services/deterministic_response_engine.py` | Plantillas + datos verificados |
| Integración | `app/api/routes/chat.py` | Desvía flujo antes del LLM |

### Fuentes de datos consumidas

- `ExecutiveSummaryRepository` — tablas `*_resumen`
- `AnalyticsService` — KPIs y resumen mensual
- `InsightsEngine` / `InsightsRepository` — hallazgos y tendencias
- `MetadataService` — cobertura temporal y contexto

## Intenciones determinísticas

| Intención | Fuente principal |
|-----------|------------------|
| TOP_CLIENTES | `cliente_resumen` |
| BOTTOM_CLIENTES | `cliente_resumen` |
| TOP_PROVEEDORES | `proveedor_resumen` |
| BOTTOM_PROVEEDORES | `proveedor_resumen` |
| TOP_CUENTAS | `cuenta_resumen` |
| BOTTOM_CUENTAS | `cuenta_resumen` |
| BEST_MONTH | `mes_resumen` |
| WORST_MONTH | `mes_resumen` |
| MONTH_ANALYSIS | `mes_resumen` + entidades |
| DATA_COVERAGE | Metadata |
| KPIS / KPIS_EJECUTIVOS | Analytics Layer |
| INSIGHTS | Insights Engine |
| CLIENTE_CRECIMIENTO / CAIDA | Insights + fact mensual |
| PROVEEDOR_CRECIMIENTO / CAIDA | Insights + fact mensual |
| RESUMEN_MENSUAL | Analytics Layer |

## Intenciones generativas

Permanecen en Ollama:

- EXECUTIVE_SUMMARY
- RISKS
- OPPORTUNITIES
- YEAR_SUMMARY
- EXECUTIVE_INSIGHTS
- BUSINESS_CONCENTRATION
- EVOLUCION_*
- UNKNOWN / baja confianza

## Observabilidad

`ChatResponse` incluye:

```json
{
  "response_mode": "DETERMINISTIC",
  "timings": {
    "deterministic_ms": 8.4,
    "llm_ms": 0
  }
}
```

## Ventajas

1. **Latencia:** respuestas en milisegundos vs segundos del LLM.
2. **Tokens:** costo cero en consultas empresariales rutinarias.
3. **Determinismo:** misma pregunta → misma respuesta verificable.
4. **Trazabilidad:** `sources` indica tablas/capas utilizadas.
5. **Producción:** desacopla narrativa factual de interpretación generativa.

## Operación

```powershell
python scripts/test_deterministic_responses.py
```

Objetivo de validación: **7/7 OK** con `response_mode=DETERMINISTIC` y `llm_ms=0`.

## Ejemplos de plantillas

**TOP_CLIENTES**

> Durante 2025 el cliente con mayor actividad fue PUBLICO EN GENERAL con 57,730 movimientos registrados, ocupando la primera posición del ranking empresarial.

**BEST_MONTH**

> Junio fue el mes con mayor actividad del ejercicio 2025 con 37,482 movimientos registrados.

**CLIENTE_CRECIMIENTO**

> El cliente con mayor crecimiento relativo fue SERVICIOS EN PUERTOS Y TERMINALES con una variación de 12,514.29%.

## Preparación para producción

- Ejecutar `build_executive_summaries.py` tras cada carga ETL.
- Monitorear ratio `DETERMINISTIC` vs `GENERATIVE` en observabilidad.
- Extender plantillas agregando intenciones al resolver sin tocar Ollama.
- Mantener KPIs ejecutivos como fuente de validación cruzada.
