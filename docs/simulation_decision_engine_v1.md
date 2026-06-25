# Simulation & Decision Engine v1

## Resumen

El **Simulation & Decision Engine** proyecta escenarios operativos y financieros utilizando exclusivamente la línea base de **Operational Metrics** y **FinOps**. No duplica cálculos financieros: reutiliza `operational_metrics.cost_engine` para costos y ahorros.

## Arquitectura

```
Operational Metrics / FinOps
        │
        ▼
repository.py (línea base histórica)
        │
   ┌────┴────┬──────────────┐
   ▼         ▼              ▼
scenario_engine  forecast_engine  decision_engine
   │                │              │
   └────────┬───────┴──────────────┘
            ▼
       service.py ──► /api/simulation/*
```

## Modelo

1. **Cargar baseline** desde registros operativos reales (mix de rutas, latencias P50/P95/P99, tokens promedio, ahorro por consulta).
2. **Aplicar escenario** (usuarios, consultas, % por canal, proveedor, concurrencia).
3. **Simular** consultas, tokens, costos y ahorros.
4. **Comparar** proveedores OpenAI, Claude, Ollama y Mock.
5. **Decidir** con recomendaciones automáticas.

## Escenarios predefinidos

| ID | Nombre | Perfil |
|----|--------|--------|
| `demo` | Demo | 10 usuarios, operación controlada |
| `piloto` | Piloto | 100 usuarios |
| `produccion` | Producción | 500 usuarios |
| `enterprise` | Enterprise | 1000 usuarios |
| `custom` | Hipótesis Personalizada | Parámetros libres |

## Fórmulas

```
consultas_día = usuarios × consultas_por_usuario
consultas_mes = consultas_día × días_laborales
consultas_llm = consultas_mes × (% executive + % legacy)
costo = consultas_llm × costo_token(proveedor)    # vía cost_engine
ahorro = consultas_determinísticas × avoided_cost   # baseline FinOps
ROI = (ahorro / costo) × 100
```

Latencias P50/P95/P99 y tokens promedio provienen del histórico cuando existe.

## Supuestos

- Sin histórico: defaults de `settings.py` (FinOps baseline).
- Infraestructura CPU/RAM/GPU: factores lineales por usuario, concurrencia y horas pico.
- Mix de rutas: normalizado al 100% si el usuario modifica porcentajes.

## API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/simulation/scenarios` | GET | Escenarios y baseline |
| `/api/simulation/run` | POST | Ejecutar simulación |
| `/api/simulation/comparison` | GET | Comparar proveedores |
| `/api/simulation/recommendations` | GET | Decision Engine |

## Observabilidad

- `simulation_runs`
- `most_used_scenario`
- `provider_selected`
- `average_projected_cost`
- `average_projected_savings`

## Limitaciones

1. Proyección de infraestructura no sustituye profiling real.
2. Costos usan tarifas FinOps, no facturación de proveedor.
3. Con histórico corto (<50 consultas) se activan advertencias de riesgo.
4. Comparación de proveedores asume mismo mix de rutas.

## Extensibilidad

Nuevos escenarios: añadir a `PREDEFINED_SCENARIOS` en `scenario_engine.py`.  
Nuevos proveedores: extender `PROVIDERS` en `forecast_engine.py` usando `cost_engine`.
