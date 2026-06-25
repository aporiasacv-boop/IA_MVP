# Business Entity Master v1

## Objetivo

Primera capa del modelo semántico empresarial: catálogo maestro **estructural** de entidades descubiertas en el diario general D365, sin clasificación de negocio (Sprint 2).

## Componentes

| Capa | Ruta |
|------|------|
| Tabla | `business_entity_master` |
| Modelo ORM | `app/models/business_entity_master.py` |
| Migración | `alembic/versions/008_create_business_entity_master.py` |
| Módulo | `app/business_entity_master/` |
| API | `GET /api/business-entities` |
| Carga | `scripts/load_business_entity_master.py` |
| UI | `/entidades` → `BusinessEntitiesPage` |

## Esquema

Clave natural: `(source_system, source_table, source_column, entity_code)`.

| Columna | Descripción |
|---------|-------------|
| `entity_id` | Surrogate key |
| `entity_code` | Código en origen D365 |
| `entity_name` | Nombre en origen |
| `source_system` | `D365_FO` |
| `source_table` | `movimientos_diario` |
| `source_column` | `account_display_value`, `cuenta_proveedor`, `cuenta_cliente` |
| `movement_count` | Líneas del diario |
| `movement_amount` | Suma ABS(monto) |
| `first_seen` / `last_seen` | Rango de fechas |
| `classification_status` | Siempre `pending` en v1 |
| `confidence` | Opcional; enriquecido desde CSV de discovery |

## Carga idempotente

```powershell
.\.venv\Scripts\python.exe scripts\load_business_entity_master.py
```

1. Extrae estadísticas desde `movimientos_diario` (autoritativo).
2. Upsert por clave natural.
3. Opcionalmente fusiona `confidence` desde `docs/entity_catalog_candidate.csv`.

## API (solo lectura)

```
GET /api/business-entities?search=&source_column=&sort_by=movement_count&page=1
GET /api/business-entities/statistics
GET /api/business-entities/{entity_code}?source_column=
```

## Observabilidad

Expuesto en `/api/metrics/summary` y `/api/analytics/report`:

- `business_entities_total`
- `business_entities_loaded`
- `duplicated_entities`
- `last_entity_refresh`

## Health checks

`BusinessEntityMasterService.validate_health()` valida:

- Nombres vacíos
- `first_seen > last_seen`
- Montos o conteos negativos

Los códigos duplicados cross-source se reportan pero no fallan el health (comportamiento esperado del GL).

## Próximo sprint (no implementado)

```
business_entity_master → Business Ontology → dim_tipo_entidad → dim_entidad
```

## Validación arquitectónica

Ver sección final del informe de implementación en el PR / chat de entrega.
