# Enterprise Knowledge Service (EKS) v1

## Resumen

El **Enterprise Knowledge Service (EKS)** centraliza todo el conocimiento empresarial en un único servicio transversal. El antiguo **Business Knowledge Runtime (BKR)** pasa a ser un componente interno (`runtime/`) del EKS.

## Arquitectura

```
Consumidores (Chat, Product Identity, Capability Discovery, …)
        │
        ▼
EnterpriseKnowledgePlatformService  ← interfaz única
        │
   ┌────┴────┬──────────┬─────────┐
   ▼         ▼          ▼         ▼
search/  repository/  cache/   runtime/
                              (matcher, responder, BKR)
        │
        ▼
providers/
  ├── KnowledgePackProvider (activo)
  ├── DatabaseProvider (planificado)
  ├── SharePointProvider (planificado)
  ├── PDFProvider (planificado)
  ├── DynamicsProvider (planificado)
  └── ConfluenceProvider (planificado)
```

### Módulos

| Módulo | Responsabilidad |
|--------|-----------------|
| `service.py` | API unificada del servicio |
| `repository/` | Acceso a documentos en cache |
| `cache/` | Cache centralizada compartida |
| `search/` | Motor de búsqueda |
| `runtime/` | BKR interno (matcher, responder) |
| `providers/` | Contratos y fuentes de conocimiento |
| `integration/consumers.py` | Hooks para consumidores enterprise |
| `api/` | REST `/api/enterprise-knowledge/*` |

## Interfaz única

Métodos expuestos por `EnterpriseKnowledgePlatformService`:

- `search()`, `get_concept()`, `get_rule()`, `get_faq()`, `get_glossary()`
- `get_examples()`, `get_executive_context()`, `get_capabilities()`
- `exists()`, `list_categories()`, `get_business_context()` (stub para EEP)
- `get_health()`, `get_statistics()`, `get_providers()`

El origen del conocimiento es transparente para los consumidores.

## Consumidores

| Consumidor | Integración |
|------------|-------------|
| Chat híbrido | `knowledge_for_chat()` |
| Product Identity | `knowledge_for_product_identity()` |
| Capability Discovery | `knowledge_for_capability_discovery()` |
| Guided Fallback | `knowledge_for_guided_fallback()` (preparado) |
| EKO | `knowledge_for_eko()` (preparado) |
| ERO | `knowledge_for_ero()` (preparado) |
| SBEP | `knowledge_for_sbep()` (preparado) |
| EEP | `knowledge_for_eep()` / `get_business_context()` |
| Executive Reasoning | `knowledge_for_executive_reasoning()` (preparado) |

## Proveedores

### Activo

- **KnowledgePackProvider**: lee `knowledge_pack/*.md`

### Planificados (solo interfaz)

- DatabaseProvider, SharePointProvider, PDFProvider, DynamicsProvider, ConfluenceProvider

Registrar un nuevo proveedor en el registry del servicio sin modificar consumidores.

## Flujo de consulta

1. El consumidor invoca `EnterpriseKnowledgePlatformService` o un hook de `integration/consumers.py`.
2. El servicio registra métricas (`knowledge_requests`, tiempos de búsqueda).
3. `cache/store` valida la firma del pack y recarga si cambió.
4. `repository` entrega documentos indexados.
5. `search` o `runtime/matcher` resuelven la respuesta.
6. La respuesta no expone la ruta física del origen al consumidor final (solo metadata interna).

## Cache

- Una sola cache en `cache/store.py`.
- Eliminada la cache duplicada de `knowledge_pack/loader.py` (`@lru_cache`).
- Todos los consumidores reutilizan la misma instancia vía el servicio.

## API REST

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/enterprise-knowledge/health` | Salud y estado del cache |
| `GET /api/enterprise-knowledge/statistics` | Estadísticas y métricas |
| `GET /api/enterprise-knowledge/providers` | Proveedores activos y planificados |
| `GET /api/enterprise-knowledge/search?q=` | Búsqueda |

La API legacy `/api/business-knowledge/*` se mantiene como fachada de compatibilidad.

## Observabilidad

Métricas agregadas:

- `knowledge_requests`
- `knowledge_provider_distribution`
- `cache_hit_rate`
- `cache_size`
- `average_search_time`
- `knowledge_sources`

## Extensibilidad

Para añadir SharePoint, Dynamics, PDF o Confluence:

1. Implementar `KnowledgeProvider` en `providers/`.
2. Registrar el proveedor en el agregador del servicio.
3. Los consumidores siguen usando la misma interfaz sin cambios.

## Compatibilidad

- **No se modificaron** ETL, Data Mart, Planner, Executor, Hybrid Router (solo integración mínima), EKO, ERO, SBEP, EEP ni AI Orchestration.
- `app/business_knowledge/` permanece como fachada legacy.
- Comportamiento funcional del chat y respuestas institucionales idéntico al BKR v1.
