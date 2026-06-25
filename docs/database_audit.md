# Database Audit — Asistente de Inteligencia Empresarial Olnatura

**Fecha:** 2026-06-23  
**Motor:** PostgreSQL + SQLAlchemy 2.x + Alembic (7 migraciones)

---

## Inventario de objetos

### Tablas con modelo ORM

| Tabla | Modelo | Archivo | Consultada por |
|-------|--------|---------|----------------|
| `movimientos_diario` | `MovimientoDiario` | `models/movimiento_diario.py` | `analytics_repository` (count); `executive_summary_service` (ETL script); **no query executor híbrido** |
| `fact_mes` | `FactMes` | `models/fact_tables.py` | Indirecto vía MVs |
| `fact_cuenta` | `FactCuenta` | idem | `metadata_repository`, insights |
| `fact_cliente` | `FactCliente` | idem | `system_repository`, metadata, insights |
| `fact_proveedor` | `FactProveedor` | idem | idem |
| `fact_divisa` | `FactDivisa` | idem | `analytics_repository` (count KPI) |
| `fact_cliente_mes` | `FactClienteMes` | idem | `insights_repository` |
| `fact_proveedor_mes` | `FactProveedorMes` | idem | `insights_repository`, `proveedor_repository` |
| `fact_cuenta_mes` | `FactCuentaMes` | idem | `insights_repository` |
| `cliente_resumen` | `ClienteResumen` | `executive_summary_tables.py` | `executive_summary_repository`, hybrid queries |
| `proveedor_resumen` | `ProveedorResumen` | idem | idem |
| `cuenta_resumen` | `CuentaResumen` | idem | idem |
| `mes_resumen` | `MesResumen` | idem | idem |
| `performance_metrics` | `PerformanceMetricRecord` | `observability/metrics_repository.py` | Observability, business analytics, operational audit |

### Vistas materializadas (sin modelo ORM dedicado)

Creadas en `alembic/versions/002_create_datamart.py` y `003_create_datamart_v2.py`:

| Vista materializada | Consultada por |
|---------------------|----------------|
| `mv_resumen_mensual` | `analytics_repository`, `metadata_repository`, `insights_repository`, `system_repository` |
| `mv_top_clientes` | `analytics_repository`, `cliente_repository`, insights |
| `mv_top_proveedores` | `analytics_repository`, `proveedor_repository`, insights |
| `mv_top_cuentas` | `analytics_repository`, insights |
| `mv_cliente_evolucion` | `analytics_repository` |
| `mv_proveedor_evolucion` | `analytics_repository` |
| `mv_cuenta_evolucion` | `analytics_repository` |

---

## Uso por flujo de aplicación

### Pipeline híbrido (producción)

| Objeto | Uso |
|--------|-----|
| `cliente_resumen`, `proveedor_resumen`, `cuenta_resumen`, `mes_resumen` | Queries ejecutivas vía `executive_summary_repository` |
| `mv_resumen_mensual`, `fact_cliente`, `fact_proveedor` | `system_repository` (DATA_COVERAGE, DATASET_INFO) |
| `mv_top_clientes`, `mv_top_proveedores` | `cliente_repository`, `proveedor_repository` |
| `performance_metrics` | **Toda** la telemetría de dashboards |

### API datamart legacy (`/api/kpis*`)

| Objeto | Uso |
|--------|-----|
| Todas las MVs + facts | `analytics_repository` |
| `movimientos_diario` | Solo conteo en KPIs |
| `fact_divisa` | Conteo |

### Sin uso aparente en runtime FastAPI

| Objeto | Observación |
|--------|-------------|
| `movimientos_diario` (lecturas analíticas profundas) | Comentario en `system_repository`: híbrido evita escanear millones de filas; ETL en scripts |
| `fact_mes` | Modelo definido; consultas directas no localizadas (posible uso indirecto) |

---

## Índices

### `movimientos_diario` (modelo ORM)

Índices declarados en `MovimientoDiario`:
- `ix_movimientos_diario_fecha`
- `ix_movimientos_diario_mes`
- `ix_movimientos_diario_anio`
- `ix_movimientos_diario_account_display_value`
- `ix_movimientos_diario_cuenta_proveedor`
- `ix_movimientos_diario_cuenta_cliente`
- `ix_movimientos_diario_numero_diario`

**Uso aparente:** Orientados a ETL (`import_excel`, `build_datamart`) y queries legacy sobre staging. El pipeline híbrido **no** consulta `movimientos_diario` directamente.

### `performance_metrics`

Creada en migración `005_create_performance_metrics.py`; ampliada en `006`, `007`.

Columnas clave: `handled_by`, `query_type`, `success`, tiempos por etapa, `suggested_questions_count`.

**Uso:** Alta — todos los dashboards post-hybrid.

---

## Migraciones Alembic

| Revisión | Archivo | Propósito |
|----------|---------|-----------|
| 001 | `create_movimientos_diario` | Staging Excel |
| 002 | `create_datamart` | Facts + MVs v1 |
| 003 | `create_datamart_v2` | MVs evolución |
| 004 | `create_executive_summaries` | Tablas resumen ejecutivo |
| 005 | `create_performance_metrics` | Observabilidad |
| 006 | `add_suggested_questions_metrics` | Columnas sugerencias |
| 007 | `add_business_analytics_columns` | Columnas analytics negocio |

---

## Modelos ORM sin referencia directa en repos híbridos

| Modelo | Estado |
|--------|--------|
| `FactMes` | Definido; uso indirecto no verificado en grep de repos |
| `FactDivisa` | Solo KPI legacy `/api/kpis` |
| `FactCuentaMes` | Insights legacy |
| `MovimientoDiario` | Staging + KPI count; no pipeline híbrido |

---

## Riesgos de datos

| Riesgo | Descripción |
|--------|-------------|
| Dualidad de fuentes | KPIs datamart vs `performance_metrics` pueden mostrar narrativas distintas |
| MVs desactualizadas | Sin job documentado en app para `REFRESH MATERIALIZED VIEW` |
| `performance_metrics` crecimiento | Sin política de retención documentada en código |
| Tablas resumen vs MVs | Solapamiento funcional entre `*_resumen` y `mv_*` |

---

## Resumen

| Categoría | Cantidad |
|-----------|----------|
| Tablas ORM | 14 |
| Vistas materializadas | 7 |
| Migraciones | 7 |
| Tablas core del hybrid | 4 resúmenes + MVs top + `performance_metrics` |
| Tablas primarias legacy API | facts + MVs (sin UI React) |
| Objetos con uso solo ETL/scripts | `movimientos_diario` (lectura profunda) |
