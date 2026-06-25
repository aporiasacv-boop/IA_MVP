# Business Analytics v1

## Propósito

Transformar la observabilidad técnica del Hybrid Router en métricas de **negocio**, **adopción** y **costo** para evaluar el valor económico real del asistente Olnatura.

Sin IA generativa en este módulo: todo se deriva de `performance_metrics`.

## Arquitectura

```
performance_metrics (PostgreSQL)
        ↓
BusinessAnalyticsRepository
        ↓
BusinessAnalyticsService
   ├─ Coverage
   ├─ Performance
   ├─ FinancialAnalyticsService
   ├─ Top Queries
   └─ Coverage Report
        ↓
GET /api/analytics/*
        ↓
Frontend Analytics Page
```

### Módulo `app/business_analytics/`

| Componente | Responsabilidad |
|------------|-----------------|
| `repository.py` | Consultas SQL agregadas |
| `service.py` | Orquestación y reporte |
| `financial_service.py` | FinOps / AI avoidance |
| `schemas.py` | Contratos API |
| `constants.py` | Rutas determinísticas |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/analytics/coverage` | Distribución por `handled_by` |
| GET | `/api/analytics/performance` | Percentiles y promedios de latencia |
| GET | `/api/analytics/financial` | AI avoidance y costos estimados |
| GET | `/api/analytics/top-queries` | Top queries con ruta y éxito |
| GET | `/api/analytics/report` | Score de cobertura y top routes |

## Métricas y fórmulas

### AI Avoidance Rate

```
(business_pipeline + slot_clarification + conversation_memory
 + capability_discovery + guided_fallback) / total_requests
```

### Legacy Dependency Rate

```
legacy_chat / total_requests
```

### Coverage Score (0–100)

```
ai_avoidance_rate × success_rate × 100
```

### Costos estimados

No se inventan costos. Configuración en `app/core/settings.py`:

- `GPT_COST_PER_1K_TOKENS`
- `CLAUDE_COST_PER_1K_TOKENS`
- `OLLAMA_COST_PER_1K_TOKENS`
- `ESTIMATED_TOKENS_PER_LEGACY_CALL`

```
estimated_*_cost = legacy_chat_requests × (tokens / 1000) × cost_per_1k
```

Si los placeholders están en `0.0`, el costo reportado es `0.0` (auditable).

### Equivalent calls

`estimated_gpt_equivalent_calls`, `estimated_claude_equivalent_calls` y `estimated_ollama_calls` usan `legacy_chat_requests`.

## Observabilidad extendida

Nuevas columnas en `performance_metrics` (migración `007`):

| Campo | Descripción |
|-------|-------------|
| `route_type` | Igual a `handled_by` |
| `response_success` | Igual a `success` |
| `deterministic_resolution` | `true` si no es `legacy_chat` |
| `used_ai` | `true` si es `legacy_chat` |

## Interpretación

| Métrica alta | Significa |
|--------------|-----------|
| AI Avoidance Rate | Más consultas resueltas sin LLM |
| Legacy Dependency Rate | Mayor dependencia de chat generativo |
| Coverage Score | Mejor cobertura determinística con éxito |

## Limitaciones

- Ventana financiera mensual: últimos 30 días calendario
- Costos requieren configuración explícita en `.env`
- No incluye costo por usuario, sesión ni ROI (ver roadmap)

## Future Financial Metrics (diseño preparado)

Espacio reservado para v2:

| Métrica futura | Fuente propuesta |
|----------------|------------------|
| Costo por consulta | `performance_metrics` + tokens reales |
| Costo por usuario | Autenticación + sesión |
| Costo por sesión | `session_id` en métricas |
| ROI | Ahorro vs baseline legacy |
| Ahorro mensual / anual | Proyección desde `estimated_*_cost` |

Contrato extensible en `FinancialAnalyticsResponse` sin romper v1.

## Pruebas

- Unitarias: `tests/test_business_analytics_service.py`
- Health: `tests/test_business_analytics_health.py`
- Integración: `tests/integration/test_business_analytics_integration.py`
- Frontend: `frontend/src/types/businessAnalytics.test.ts`

## Health Validation

1. `total_requests >= suma de rutas`
2. Porcentajes suman ~100%
3. `ai_avoidance_rate` ∈ [0, 1]
4. `coverage_score` ∈ [0, 100]
5. Costos no negativos
