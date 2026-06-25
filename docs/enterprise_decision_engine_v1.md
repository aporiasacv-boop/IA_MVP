# Enterprise Decision Engine v1

## Propósito

El **Enterprise Decision Engine (EDE)** convierte información, evidencia, simulaciones y métricas existentes en **recomendaciones ejecutivas fundamentadas**. No genera conocimiento nuevo ni utiliza LLM para inferir conclusiones.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enterprise Decision Engine                    │
├─────────────────────────────────────────────────────────────────┤
│  API (/api/decision/*)                                           │
│       ↓                                                          │
│  EnterpriseDecisionService                                       │
│       ↓                                                          │
│  EnterpriseDecisionRepository (solo lectura)                     │
│       ↓                                                          │
│  Analizadores → DecisionEngine → Enterprise Decision Package    │
└─────────────────────────────────────────────────────────────────┘
         ↑ consume (read-only)
┌────────┴────────┬──────────┬─────────┬──────────┬───────────────┐
│ EKS │ EKO │ ERO │ EEP │ Operational Metrics │ FinOps │ Simulation │
└─────────────────────────────────────────────────────────────────┘
```

### Módulos

| Módulo | Responsabilidad |
|--------|-----------------|
| `repository.py` | Recopila contexto de todas las fuentes autorizadas |
| `evidence_analyzer.py` | Transforma datos en ítems de evidencia trazables |
| `financial_analyzer.py` | Calcula impacto financiero desde FinOps/Simulación |
| `simulation_analyzer.py` | Extrae hallazgos y recomendaciones de escenarios |
| `recommendation_engine.py` | Aplica reglas determinísticas por tipo de decisión |
| `decision_engine.py` | Ensambla el EDP y valida evidencia obligatoria |
| `service.py` | Fachada pública y métricas de uso |
| `metrics.py` | Observabilidad: solicitudes, confianza, impacto |

## Flujo de decisión

1. El cliente invoca `POST /api/decision/recommend` con `decision_type` y `scenario_id`.
2. El repositorio consulta en modo lectura EKS, EKO, ERO, EEP, Operational Metrics, FinOps y Simulation Engine.
3. Los analizadores producen evidencia, impacto financiero y hallazgos.
4. El motor de recomendación aplica reglas por tipo de decisión.
5. Si no hay evidencia, se rechaza la solicitud (HTTP 422).
6. Se emite un **Enterprise Decision Package (EDP)** con trazabilidad completa.

## Tipos de decisión soportados

- `proveedor_ia` — Proveedor IA recomendado
- `escenario` — Escenario recomendado
- `infraestructura` — Infraestructura recomendada
- `estrategia_despliegue` — Estrategia de despliegue
- `optimizacion_costos` — Optimización de costos
- `optimizacion_ia` — Optimización del uso de IA
- `optimizacion_pipeline` — Optimización del Pipeline

## Evidencia

Cada ítem de evidencia incluye:

- `source` — Fuente de datos (ej. `finops`, `simulation_engine`)
- `metric` — Métrica utilizada
- `value` — Valor observado
- `rule` — Regla determinística que participó
- `confidence` — Nivel de confianza del dato (0–1)

Toda recomendación principal vincula `evidence_ids`. Sin evidencia no se emite recomendación.

## Criterios de decisión

Las reglas son **100 % determinísticas**:

- Comparativa de proveedores desde Simulation Engine + histórico FinOps
- Mix de rutas operativas desde Operational Metrics
- Proyección de costo/ahorro desde simulación y FinOps
- Calidad de objetos EKO/ERO/EEP cuando la base de datos está disponible

## API

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/decision/recommend` | Genera un EDP |
| GET | `/api/decision/schema` | Esquema del paquete |
| GET | `/api/decision/statistics` | Métricas del motor |
| GET | `/api/decision/example` | Ejemplo de EDP |

## Frontend

Pantalla **Centro de Decisiones** (`/centro-decisiones`): resumen ejecutivo, recomendación principal, alternativas, impacto económico, riesgos, oportunidades, evidencia y confianza.

## Observabilidad

Expuesto en `/api/decision/statistics` y `/api/metrics/summary`:

- `decision_requests`
- `recommendation_types`
- `average_confidence`
- `average_financial_impact`
- `decision_sources`

## Limitaciones v1

- Requiere al menos una fuente con datos (simulación siempre activa; operación mejora confianza).
- EKO/ERO/EEP dependen de sesión de base de datos.
- No ejecuta acciones: solo recomienda.
- No modifica ETL, Data Mart, Pipeline, Planner, Executor ni AI Orchestration.
- Decisiones estratégicas de negocio (prioridades corporativas, compliance regulatorio específico) requieren criterio humano.

## Restricciones de salida

El EDP **nunca** incluye SQL, prompts ni detalles de implementación interna.
