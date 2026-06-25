# Canonical Business Entity v1

## Objetivo

Resolver identidades empresariales únicas antes de construir la Ontología Empresarial (Sprint 3).

## Modelo

```
business_entity_master (sin modificar)
        ↓ business_entity_resolution (1:1)
canonical_business_entity
        ↑
canonical_entity_suggestion (pares pendientes, sin merge auto)
```

## Tablas

| Tabla | Rol |
|-------|-----|
| `canonical_business_entity` | Organización única |
| `business_entity_resolution` | Puente 1:1 entidad → canónica |
| `canonical_entity_suggestion` | Candidatos de unión con regla y score |

## Reglas de sugerencia (determinísticas)

| Regla | Score típico | Evidencia |
|-------|--------------|-----------|
| `rfc_exact` | 0.95 | Mismo RFC en código o nombre |
| `normalized_name_exact` | 0.90 | Nombre normalizado idéntico |
| `token_overlap` | 0.70–0.85 | Tokens significativos compartidos |
| `fuzzy_name_similarity` | 0.82+ | Similitud de cadena |
| `brand_token_match` | 0.88 | Token de marca ≥5 chars (ej. WALMART) |

**No se fusionan entidades automáticamente.** Solo `singleton_bootstrap`: cada entidad comercial obtiene su propia canónica hasta revisión humana.

## Alcance comercial

Solo `cuenta_cliente` y `cuenta_proveedor`. Las cuentas contables (`account_display_value`) quedan fuera de resolución canónica.

## API (solo lectura)

```
GET /api/canonical-entities
GET /api/canonical-entities/suggestions
GET /api/canonical-entities/statistics
```

## Carga idempotente

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe scripts\generate_canonical_suggestions.py
```

## UI

Ruta `/canonicas` — entidades canónicas, alias y sugerencias pendientes.

## Observabilidad

- `canonical_entities_total`
- `canonical_matches` (canónicas con >1 alias resuelto)
- `pending_matches`
- `automatic_suggestions`

## Health checks

- Entidades comerciales huérfanas (sin resolución)
- Resoluciones duplicadas por entity_id
- Scores fuera de [0, 1]

## Próximo sprint

Ontología empresarial sobre identidades canónicas validadas — **no implementado aquí**.
