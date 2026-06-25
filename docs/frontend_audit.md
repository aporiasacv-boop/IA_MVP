# Frontend Audit — Asistente de Inteligencia Empresarial Olnatura

**Fecha:** 2026-06-23  
**Stack:** React 19 + TypeScript + Vite + React Router 7

---

## Arquitectura general

```
main.tsx → App.tsx → AppLayout (Sidebar + Outlet)
    ├── /              AssistantPage
    ├── /rendimiento   PerformancePage
    ├── /analytics     AnalyticsPage
    └── /audit         OperationalAuditPage
```

Patrón consistente: **Page → Hook → Service → API**.

---

## Pages

| Página | Ruta | Hook(s) | Clasificación |
|--------|------|---------|---------------|
| `AssistantPage` | `/` | `useChatApi`, `useScrollToBottom` | **ACTIVO** |
| `PerformancePage` | `/rendimiento` | `usePerformanceMetrics`, `useBackendMetrics` | **ACTIVO** |
| `AnalyticsPage` | `/analytics` | `useBusinessAnalytics` | **ACTIVO** |
| `OperationalAuditPage` | `/audit` | `useOperationalAudit` | **ACTIVO** |
| `OperationalAuditPage.test.tsx` | — | — | Test |

---

## Components (33 archivos)

### ACTIVO — 30 componentes

| Área | Componentes |
|------|-------------|
| Layout | `AppLayout`, `Sidebar` |
| Assistant (11) | `ConversationView`, `AssistantMessage`, `UserMessage`, `ChatInput`, `EmptyState`, `QuickSuggestions`, `RecentQueries`, `ExecutiveText`, `ResponseOriginBadge`, `HybridTechnicalDetails`, `TechnicalDetails`, `SuggestedQuestionsFollowUp` |
| Performance (4 usados) | `BackendMetricsSection`, `ExecutiveSummarySection`, `SmartSavingsHero`, `ArchitecturalExplanation` |
| Analytics (5) | `AnalyticsCard`, `CoverageDashboard`, `FinancialDashboard`, `PerformanceDashboard`, `TopQueriesDashboard` |
| Operational Audit (5) | `AuditOverviewSection`, `CoverageGapsTable`, `TopFailuresTable`, `TopRoutesTable`, `AdoptionSection` |

### NO UTILIZADO — 3 componentes

| Componente | Sustituto funcional | Evidencia |
|------------|---------------------|-----------|
| `PerformanceMetricsGrid` | `ExecutiveSummarySection` (grilla inline) | 0 imports en `src/` |
| `CostOptimizationSection` | Ninguno en UI actual | 0 imports |
| `PerformanceHero` | Título en `ExecutiveSummarySection` / hero de `SmartSavingsHero` | 0 imports |

### LEGACY

| Elemento | Estado |
|----------|--------|
| `constants/suggestions.ts` → `QUICK_SUGGESTIONS` | Deprecado; sugerencias vienen del backend |
| `sendLegacyChatQuestion` en `chatApi.ts` | Activo como fallback cuando hybrid deshabilitado |

---

## Hooks (6)

| Hook | Consumidor | Clasificación |
|------|------------|---------------|
| `useChatApi` | `AssistantPage` | **ACTIVO** |
| `useScrollToBottom` | `AssistantPage` | **ACTIVO** |
| `usePerformanceMetrics` | `PerformancePage` | **ACTIVO** |
| `useBackendMetrics` | `PerformancePage` | **ACTIVO** |
| `useBusinessAnalytics` | `AnalyticsPage` | **ACTIVO** |
| `useOperationalAudit` | `OperationalAuditPage` | **ACTIVO** |

---

## Services (6)

| Servicio | HTTP | Almacenamiento local | Clasificación |
|----------|------|---------------------|---------------|
| `chatApi.ts` | `/api/chat`, `/api/chat/hybrid` | — | **ACTIVO** |
| `metricsApi.ts` | 3 endpoints metrics | — | **ACTIVO** |
| `businessAnalyticsApi.ts` | 5 endpoints analytics | — | **ACTIVO** |
| `operationalAuditApi.ts` | 6 endpoints audit | — | **ACTIVO** |
| `performanceApi.ts` | Via chatApi | `sessionStorage` | **ACTIVO** |
| `performanceStore.ts` | — | `localStorage` | **ACTIVO** |

### Gap de integración

| Dato | Obtenido | Mostrado en UI |
|------|----------|----------------|
| `CoverageReport` | `useBusinessAnalytics` | **No** (`AnalyticsPage` ignora `data.report`) |
| `/api/metrics/routing` | No hay servicio | — |
| `/api/audit/report` | No hay servicio | — |

---

## Types

| Archivo | Tipos principales | Clasificación |
|---------|-------------------|---------------|
| `chat.ts` | `ChatMessage`, `ChatApiResponse`, etc. | **ACTIVO** |
| `hybrid-chat.ts` | `HybridChatResult` | **ACTIVO** |
| `performance.ts` | `PerformanceMetrics`, `SavingsExample` | **ACTIVO**; `CostOptimizationExample` **NO UTILIZADO** |
| `metrics.ts` | `MetricsSummary`, `PerformanceStats` | **ACTIVO**; `RoutingMetrics` y relacionados **NO UTILIZADO** |
| `businessAnalytics.ts` | Analytics DTOs | **ACTIVO**; `CoverageReport` sin UI |
| `operationalAudit.ts` | Audit DTOs | **ACTIVO** |

---

## i18n

| Módulo | Estado |
|--------|--------|
| `i18n/spanish.ts` | **ACTIVO** — catálogo centralizado Español v1 |
| `i18n/spanish.test.ts` | Tests |
| `translateDomain` | Export sin uso en UI (solo tests) |

---

## Configuración

| Archivo | Propósito | Clasificación |
|---------|-----------|---------------|
| `config/featureFlags.ts` | `USE_HYBRID_CHAT`, `DEBUG_MODE` | **ACTIVO** |
| `constants/suggestions.ts` | Quick suggestions deprecadas | **LEGACY** |

---

## Assets

| Asset | Referenciado | Estado |
|-------|--------------|--------|
| `/olnat-logo.png` | `Sidebar`, `EmptyState` | Referenciado; **ausente en `public/`** (solo `favicon.svg`, `icons.svg`) |
| `src/assets/vite.svg` | No | **NO UTILIZADO** |
| `public/icons.svg` | No | **NO UTILIZADO** |

---

## Resumen cuantitativo

| Categoría | Activos | Legacy | No utilizados |
|-----------|---------|--------|---------------|
| Pages | 4 | 0 | 0 |
| Components | 30 | 0 | 3 |
| Hooks | 6 | 0 | 0 |
| Services | 6 | 0 | 0 |
| Types (exports directos) | ~18 | 1 constante | ~4 interfaces |
| Endpoints HTTP únicos llamados | 17 | 1 condicional legacy | 2+ no integrados |

---

## Deuda frontend principal

1. **Tres componentes de performance huérfanos** — código duplicado o iteración incompleta.
2. **Fetch de `CoverageReport` sin presentación** — trabajo de backend desperdiciado en cliente.
3. **Tipos `RoutingMetrics` sin servicio** — desalineación con `/api/metrics/routing`.
4. **Asset de logo posiblemente faltante** en build estático.
