# Business Knowledge Runtime v1

Runtime unificado que consolida el conocimiento institucional desde `knowledge_pack/` para respuestas conversacionales, APIs y la pantalla `/conocimiento`.

## Arquitectura

```
knowledge_pack/          (fuente única de verdad en Markdown)
    │
    ▼
app/business_knowledge/
    ├── loader.py        Carga, índice FAQ, capacidades, cache por mtime
    ├── matcher.py       Resolución de preguntas institucionales
    ├── runtime.py       Servicio público (search, categories, stats)
    ├── responder.py     Integración con hybrid chat
    └── metrics.py       Hits, misses, cache, reload
```

No modifica EKO, ERO, SBEP, EEP, AI Orchestration, Planner, Executor ni Business Pipeline.

## Flujo conversacional

```
Usuario
  → Product Identity (patrones; texto desde FAQ)
  → Business Knowledge Runtime (FAQ, capacidades, definiciones)
  → Hybrid Router
      → Business Pipeline
      → Executive Reasoning
      → Guided Fallback
      → Legacy (último recurso)
```

`capability_discovery` ya no intercepta antes del pipeline: las capacidades se leen de `knowledge_pack/executive/capacidades-asistente.md`.

`SYSTEM_CAPABILITIES` del planner redirige al runtime en lugar de ejecutar plantillas hardcodeadas.

## Cache

- Índice en memoria con invalidación automática al cambiar el `mtime` de cualquier `.md` en `knowledge_pack/`.
- Métricas: `knowledge_runtime_hits`, `knowledge_runtime_misses`, `knowledge_runtime_cache_hits`, `knowledge_runtime_reload_time`, `knowledge_runtime_last_refresh`.

## APIs

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/business-knowledge/health` | Estado del runtime y del pack |
| `GET /api/business-knowledge/statistics` | Documentos, FAQ, métricas |
| `GET /api/business-knowledge/search?q=` | Búsqueda en todo el pack |
| `GET /api/business-knowledge/categories` | Resumen por categoría |

Observabilidad integrada en `/api/metrics/summary` y `/api/analytics/report`.

## Integración

- `hybrid_chat.py`: identity → BKR → router
- `product_identity/`: sin texto duplicado; delega al runtime
- `capability_discovery/v2/`: payload desde el pack
- `social_identity_layer.py`: saludos e identidad desde FAQ
- Frontend: `/conocimiento` (BKR); EKO en `/objetos-conocimiento`

## Ventajas

- Una sola fuente de verdad para identidad, FAQ y capacidades
- Actualización del pack sin redeploy de respuestas hardcodeadas
- Trazabilidad (`knowledge_source`, `knowledge_match_type` en metadata)
- Pantalla ejecutiva de exploración del conocimiento
