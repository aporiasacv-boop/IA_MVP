# Semantic Business Ontology v1

## Objetivo

Capa semántica que explica **qué representa** cada entidad canónica en el negocio, basada en **comportamiento** (Business Entity Profile), no en nombre.

## Modelo conceptual (separado)

| Concepto | Pregunta | Ejemplos |
|----------|----------|----------|
| **Identity** | ¿Quién es? | Organización, Parte comercial, Cuenta contable |
| **Role** | ¿Qué función? | Cliente, Proveedor, Banco, Empleado |
| **Nature** | ¿Qué representa contablemente? | Activo, Pasivo, Ingreso, Gasto |
| **Behavior** | ¿Cómo participa? | Compra, Venta, Cobro, Pago, Mixto |

## Tablas

| Tabla | Rol |
|-------|-----|
| `business_ontology_type` | Taxonomía editable |
| `business_ontology_rule` | Reglas determinísticas |
| `business_ontology_assignment` | Sugerencias (pending/approved/rejected) |

## Motor de ontología

- **Sin LLM** — solo reglas sobre perfil + dimensiones + cuentas top
- **Sin clasificación automática** — todo queda en `status=pending`
- Evidencia JSON en cada asignación
- Idempotente vía `upsert` por `(canonical_id, concept_category, type_id, rule_code)`

## Reglas principales

| Categoría | Regla ejemplo | Evidencia |
|-----------|---------------|-----------|
| Role | `role_client_dimension` | `dimensions_used = [cuenta_cliente]` |
| Role | `role_dual_commercial` | cliente + proveedor |
| Nature | `nature_income_prefix` | >50% movimientos en cuentas 4xx |
| Behavior | `behavior_payment` | proveedor + débito > crédito |

## API (solo lectura)

```
GET /api/business-ontology
GET /api/business-ontology/types
GET /api/business-ontology/assignments
GET /api/business-ontology/statistics
```

## Generación

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe scripts\generate_entity_profiles.py
.\.venv\Scripts\python.exe scripts\generate_ontology_suggestions.py
```

## UI

Ruta `/ontologia` — entidad, identidad, perfil resumido, sugerencias con evidencia y score.

## Observabilidad

- `ontology_entities`, `ontology_pending`, `ontology_approved`, `ontology_rules`, `ontology_average_confidence`

## Próximos consumidores (no implementados)

- Business Knowledge Layer
- Semantic Data Mart
- Intent Engine v2
- Executive Reasoning
