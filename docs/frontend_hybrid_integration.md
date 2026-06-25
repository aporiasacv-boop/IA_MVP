# Integración Frontend — Hybrid Chat y Métricas Reales

Este documento describe cómo el frontend del **Asistente de Inteligencia Empresarial Olnatura** consume el Hybrid Router y las métricas de observabilidad del backend, manteniendo compatibilidad con el chat legacy.

## Feature Flag: `USE_HYBRID_CHAT`

| Variable de entorno | Valor por defecto | Efecto |
|---------------------|-------------------|--------|
| `VITE_USE_HYBRID_CHAT` | `true` (habilitado si no se define) | Usa `POST /api/chat/hybrid` |
| `VITE_USE_HYBRID_CHAT=false` | — | Vuelve a `POST /api/chat` (legacy) |

Configuración en `frontend/src/config/featureFlags.ts` y `.env`:

```env
VITE_USE_HYBRID_CHAT=true
```

**Rollback inmediato:** cambiar a `false`, reiniciar el dev server o reconstruir el bundle. No requiere cambios de código.

### Modo debug

| Variable | Valor | Efecto |
|----------|-------|--------|
| `VITE_DEBUG_MODE=true` | — | Muestra panel técnico e indicador de origen en el chat |
| `VITE_DEBUG_MODE=false` | por defecto | UX ejecutiva sin detalles técnicos |

## Flujo Hybrid Chat

```
Usuario → sendChatQuestion()
              │
              ├─ USE_HYBRID_CHAT=true  → POST /api/chat/hybrid { message }
              │                              │
              │                              ├─ business_pipeline → respuesta determinística
              │                              └─ legacy_chat       → delega a /api/chat interno
              │
              └─ USE_HYBRID_CHAT=false → POST /api/chat { question }
```

### Contrato de respuesta (`HybridChatResult`)

```json
{
  "handled_by": "business_pipeline",
  "success": true,
  "answer": "Actualmente existen 50 clientes registrados.",
  "metadata": {
    "query_type": "COUNT_CLIENTES",
    "confidence": 1.0
  }
}
```

El hook `useChatApi` mapea internamente a `ChatMessage` para que el usuario siga viendo pregunta y respuesta sin cambios.

Archivos clave:

- `src/services/chatApi.ts` — enrutamiento y mapeo
- `src/types/hybrid-chat.ts` — tipos
- `src/hooks/useChatApi.ts` — orquestación del chat

## Métricas reales del backend

Endpoints consumidos por `src/services/metricsApi.ts`:

| Método | Endpoint | Uso |
|--------|----------|-----|
| `getSummary()` | `GET /api/metrics/summary` | Totales pipeline vs legacy |
| `getPerformance()` | `GET /api/metrics/performance` | P50, P95, P99 |
| `getTopQueries()` | `GET /api/metrics/top-queries` | Preguntas más frecuentes |

La pantalla **Performance** muestra dos bloques separados:

1. **Métricas reales backend** — datos persistidos por el Hybrid Router (`BackendMetricsSection`)
2. **Métricas locales frontend** — localStorage + benchmark de sesión (`ExecutiveSummarySection`, sin cambios funcionales)

## Compatibilidad

| Capacidad | Estado |
|-----------|--------|
| `POST /api/chat` directo | Disponible vía `sendLegacyChatQuestion()` y flag `false` |
| Métricas locales (localStorage) | Conservadas en `performanceStore.ts` |
| Benchmark de sesión | Conservado en `performanceApi.ts` |
| Panel técnico legacy (timings) | Visible cuando la respuesta legacy incluye `timings` |
| Registro local híbrido | `recordHybridResponse()` mapea pipeline → determinístico |

## Rollback

1. En `.env` del frontend: `VITE_USE_HYBRID_CHAT=false`
2. Reiniciar: `npm run dev` o redeploy del build
3. El chat vuelve a `POST /api/chat` sin tocar backend ni eliminar código híbrido

Para desactivar UI de debug: `VITE_DEBUG_MODE=false`.

## Pruebas

```bash
cd frontend
npm run test
```

Cubre:

- Resolución del feature flag
- Mapeo `HybridChatResult` → `ChatMessage`
- Compatibilidad de métricas locales con respuestas híbridas
- Contratos TypeScript de métricas del backend
