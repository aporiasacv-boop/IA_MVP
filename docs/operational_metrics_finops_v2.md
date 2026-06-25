# Operational Metrics & FinOps v2

## Resumen

El módulo `app/operational_metrics/` consolida evidencia operativa y financiera por consulta. Reemplaza estimaciones agregadas cuando existen registros reales capturados en el flujo híbrido.

## Arquitectura

```
POST /api/chat/hybrid
        │
        ▼
collector.py ──► repository.py (memoria + PostgreSQL)
        │                 │
        ▼                 ▼
   cost_engine.py    aggregator.py ──► service.py ──► /api/finops/*
        │
 forecast_engine.py
```

## Modelo financiero

Cada consulta genera un `OperationalQueryRecord` con:

- Identidad: `request_id`, `timestamp`, `session_id`, `user_id`, `channel`
- Ruteo: `handled_by`, `query_type`, `intent`, `verb`
- Tokens: `input_tokens`, `output_tokens`, `total_tokens`, `estimated_tokens`, `token_source`
- Costos: `cost_usd`, `cost_mxn`, `avoided_cost_usd`
- Flags: `llm_used`, `knowledge_hit`, `pipeline_hit`, `executive_reasoning`, `cache_hit`

## Fórmulas

### Costo real por consulta LLM

```
cost_usd = (input_tokens / 1000) * rate_input + (output_tokens / 1000) * rate_output
```

Tarifas en `settings.py` por proveedor (OpenAI, Claude, Ollama).

### Costo evitado (consultas determinísticas)

```
avoided_cost_usd = benchmark_cost_openai(baseline_input, baseline_output)
```

Baseline configurable: `FINOPS_BASELINE_INPUT_TOKENS`, `FINOPS_BASELINE_OUTPUT_TOKENS`.

### Conversión MXN

```
cost_mxn = cost_usd * USD_TO_MXN_RATE
```

### LLM Avoidance

```
llm_avoidance_rate = consultas_sin_llm / total_consultas
```

Rutas LLM: `legacy_chat`, `executive_reasoning`.

## Supuestos

| Parámetro | Default | Uso |
|-----------|---------|-----|
| `USD_TO_MXN_RATE` | 17.5 | Conversión |
| `FINOPS_BASELINE_INPUT_TOKENS` | 800 | Ahorro evitado |
| `FINOPS_BASELINE_OUTPUT_TOKENS` | 400 | Ahorro evitado |
| `FINOPS_QUERIES_PER_USER_DAY` | 12 | Forecast sin histórico |

## Forecast

Escenarios para 100, 500, 1000, 5000 y 10000 usuarios:

- Consultas mensuales = usuarios × consultas/día × 30
- Costo por proveedor = consultas × costo unitario benchmark
- CPU/RAM/GPU = factores lineales por usuario (proyección de capacidad)

Con histórico real, `ForecastEngine.from_records()` ajusta tokens y latencia promedio.

## ROI / Ahorro

- **LLM Avoidance**: consultas resueltas sin `legacy_chat` ni `executive_reasoning`
- **Knowledge Avoidance**: `product_identity`, `business_knowledge`
- **Pipeline Avoidance**: `business_pipeline`
- **Costo evitado acumulado**: suma de `avoided_cost_usd`

## API

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/finops/overview` | Resumen ejecutivo |
| `GET /api/finops/costs` | Desglose multidimensional |
| `GET /api/finops/providers` | Comparativa proveedores |
| `GET /api/finops/forecast` | Simulación de capacidad |
| `GET /api/finops/savings` | Ahorro por canal |
| `GET /api/finops/trends` | Tendencias diarias/mensuales |

## Consolidación observabilidad

- `FinancialAnalyticsService` usa FinOps cuando hay registros reales
- `MetricsService` expone `operational_*` como fuente única financiera en proceso
- Tabla `operational_query_metrics` (migración 014) para persistencia

## Limitaciones

1. **Legacy chat**: tokens estimados por longitud de texto si la API no devuelve usage
2. **Costo USD**: calculado con tarifas configuradas, no facturación real de proveedor
3. **Forecast CPU/RAM/GPU**: proyección lineal, no profiling de infraestructura
4. **Usuario**: opcional; sin autenticación se registra como anónimo
5. **Histórico**: memoria en proceso + DB; reinicio pierde memoria si DB no migrada

## Integración

Captura en `app/api/routes/hybrid_chat.py` sin modificar Planner, Executor ni Business Pipeline.
