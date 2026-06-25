# Executive Summary Layer

## Objetivo

Construir una capa ejecutiva de resúmenes empresariales pre-calculados que permita responder consultas frecuentes sin recorrer tablas detalladas (`movimientos_diario`) ni depender del flujo generativo con LLM.

Esta capa materializa métricas de negocio listas para consumo por el **Deterministic Response Engine** en un sprint posterior.

## Arquitectura

```
movimientos_diario
        │
        ▼
   fact_* (datamart)
        │
        ▼
 executive_summary_service  ──►  rebuild / truncate
        │
        ▼
┌───────────────────────────────────────────────────┐
│ cliente_resumen   │ proveedor_resumen             │
│ cuenta_resumen    │ mes_resumen                   │
└───────────────────────────────────────────────────┘
        │
        ▼
 executive_summary_repository  ──►  consultas top/bottom/resumen
        │
        ▼
 Deterministic Response Engine (futuro)
```

### Tablas

| Tabla | Granularidad | Campos clave |
|-------|--------------|--------------|
| `cliente_resumen` | Cliente | ranking, participacion_pct, primer/ultimo movimiento |
| `proveedor_resumen` | Proveedor | ranking, participacion_pct, primer/ultimo movimiento |
| `cuenta_resumen` | Cuenta contable | ranking, participacion_pct |
| `mes_resumen` | Periodo mensual | ranking_actividad, ranking_volumen, nombre_mes |

### Fuentes de datos

- **Agregaciones base:** `fact_cliente`, `fact_proveedor`, `fact_cuenta`, `fact_mes`
- **Fechas de actividad:** `movimientos_diario` (solo cliente y proveedor)
- **Referencia cruzada:** KPIs ejecutivos vía `mv_top_*` y `mv_resumen_mensual`

### Cálculos

- **participacion_pct:** volumen de la entidad / volumen total de su dimensión × 100
- **ranking:** descendente por `movimientos`, desempate por `monto_total`
- **mes_resumen.ranking_actividad:** descendente por movimientos
- **mes_resumen.ranking_volumen:** descendente por monto_total

## Componentes

| Componente | Ruta | Responsabilidad |
|------------|------|-----------------|
| Modelos | `app/models/executive_summary_tables.py` | Definición ORM de las 4 tablas |
| Repositorio | `app/repositories/executive_summary_repository.py` | Lectura de resúmenes y top/bottom |
| Servicio | `app/services/executive_summary_service.py` | Construcción y refresco de tablas |
| Build | `scripts/build_executive_summaries.py` | Pipeline operativo de reconstrucción |
| Validación | `scripts/validate_executive_summaries.py` | Cruce contra KPIs ejecutivos |

## Beneficios

1. **Latencia mínima:** consultas O(1) o O(n pequeño) sobre tablas indexadas.
2. **Determinismo:** mismos datos, misma respuesta; sin variabilidad del LLM.
3. **Costo cero de tokens:** no requiere contexto generativo para preguntas ejecutivas.
4. **Alineación con KPIs:** validación automática contra `fetch_kpis_ejecutivos()`.
5. **Preparación semántica:** rankings, participación y fechas ya resueltos para plantillas futuras.

## Casos de uso

| Pregunta empresarial | Tabla / método |
|---------------------|----------------|
| ¿Quién es el cliente principal? | `obtener_top_clientes_resumen(1)` |
| ¿Cuáles son los clientes con menor actividad? | `obtener_bottom_clientes_resumen(n)` |
| ¿Quién es el proveedor principal? | `obtener_top_proveedores_resumen(1)` |
| ¿Qué cuenta concentra más movimientos? | `obtener_cuenta_resumen()` ranking=1 |
| ¿Cuál fue el mes con mayor actividad? | `mes_resumen` WHERE ranking_actividad=1 |
| ¿Cuál fue el mes con mayor volumen? | `mes_resumen` WHERE ranking_volumen=1 |
| ¿Qué participación tiene un cliente? | `cliente_resumen.participacion_pct` |

## Operación

### Migración

```bash
alembic upgrade head
```

### Construcción

```bash
python scripts/build_executive_summaries.py
```

### Validación

```bash
python scripts/validate_executive_summaries.py
```

## Preparación para Deterministic Response Engine

El motor determinístico (sprint futuro) podrá:

1. Mapear intenciones del router (`TOP_CLIENTES`, `BOTTOM_PROVEEDORES`, `BEST_MONTH`, etc.) a métodos del repositorio.
2. Formatear respuestas desde filas pre-calculadas sin SQL dinámico ni LLM.
3. Reutilizar `participacion_pct` y `ranking` para narrativas ejecutivas consistentes.
4. Invocar `ExecutiveSummaryService.rebuild_all()` tras cargas ETL o refresh del datamart.

## Alcance de este sprint

- Solo capa de datos.
- Sin integración con Chat, Intent Router, Ollama, Prompt Builder ni Response Generator.
- Sin plantillas de respuesta ni generación de texto.
