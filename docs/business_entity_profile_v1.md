# Business Entity Profile v1

## Objetivo

Descubrir el comportamiento transaccional real de cada entidad canónica en el diario general, **sin clasificación por nombre**, como prerequisito de la Business Ontology.

## Modelo

```
canonical_business_entity (1)
        ↓
business_entity_profile (1)
        ↑ calculado desde movimientos_diario vía business_entity_resolution + business_entity_master
```

## Métricas calculadas (solo datos PostgreSQL)

| Métrica | Fuente |
|---------|--------|
| `total_movements` | COUNT movimientos vinculados |
| `total_amount` | SUM(`monto`) |
| `average_amount` | AVG(`monto`) |
| `first_seen` / `last_seen` | MIN/MAX(`fecha`) |
| `active_months` | DISTINCT `anio`+`mes` |
| `active_days` | DISTINCT `fecha` |
| `monthly_distribution` | JSON por periodo YYYY-MM |
| `debit_amount` / `credit_amount` | SIGNO de `monto` (>0 débito, <0 crédito) |
| `debit_credit_ratio` | débito / crédito |
| `related_accounts_count` | DISTINCT `account_display_value` |
| `related_counterparties_count` | DISTINCT códigos cliente/proveedor ajenos al alias propio |
| `currencies` | DISTINCT `divisa` |
| `journals` | DISTINCT `numero_diario` + top 10 |
| `dimensions_used` | `source_column` de alias en master |
| `top_accounts` / `top_counterparties` | Top 10 por volumen |

## API (solo lectura)

```
GET /api/entity-profiles
GET /api/entity-profiles/{canonical_id}
GET /api/entity-profiles/statistics
```

## Generación idempotente

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe scripts\generate_entity_profiles.py
```

Recalcula todos los perfiles por `canonical_id` sin duplicar filas (upsert).

## UI

Ruta `/perfiles` — resumen ejecutivo, lista, detalle con actividad, montos, cuentas, distribución mensual y contrapartes.

## Observabilidad

- `entity_profiles_total`
- `average_profile_completeness`
- `profile_generation_time`
- `last_profile_refresh`

## Health checks

- Montos inconsistentes (`debit - credit ≠ total`)
- Fechas inválidas (`first_seen > last_seen`)
- Distribución mensual incompleta
- Perfiles sin movimientos (informativo)
- Entidades activas sin relaciones

## Próximo sprint

Business Ontology sobre perfiles validados — **no implementado aquí**.
