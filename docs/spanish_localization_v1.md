# Localización Español v1

Objetivo: **cero inglés visible** para usuarios de negocio (Dirección, Finanzas, Operaciones, Compras). Cambios **solo de presentación** en frontend — sin modificar APIs, base de datos ni observabilidad backend.

## Enfoque

| Principio | Implementación |
|-----------|----------------|
| Catálogo único | `frontend/src/i18n/spanish.ts` |
| Backend intacto | `handled_by`, `query_type` siguen en inglés en API |
| Presentación | Funciones `translateHandledBy()`, `translateQueryType()`, etc. |
| Tooltips ejecutivos | `METRIC_TOOLTIPS` en tarjetas de analítica y auditoría |
| Exportaciones | Localización en cliente al descargar CSV/JSON |

## Elementos traducidos

### Navegación

| Antes | Después |
|-------|---------|
| Analytics | Analítica Empresarial |
| Operational Audit | Auditoría Operacional |
| Asistente IA | Asistente IA *(sin cambio)* |
| Rendimiento | Rendimiento *(sin cambio)* |

### Canales (`handled_by`)

| Valor API | Etiqueta visible |
|-----------|------------------|
| `business_pipeline` | Canal Empresarial |
| `conversation_memory` | Memoria Conversacional |
| `slot_clarification` | Aclaración de Consulta |
| `guided_fallback` | Asistencia Guiada |
| `capability_discovery` | Descubrimiento de Capacidades |
| `legacy_chat` | Conversación General |

### Analítica Empresarial

| Antes | Después |
|-------|---------|
| Coverage Score | Cobertura Operativa |
| Coverage Gap Score | Brecha de Cobertura |
| Success Rate | Tasa de Éxito |
| Average Response Time | Tiempo Promedio de Respuesta |
| Top Queries | Consultas Más Frecuentes |
| Top Domains | Dominios Más Consultados |
| AI Avoidance Rate | Consultas Resueltas Sin IA |
| Legacy Dependency Rate | Dependencia de IA Conversacional |
| Estimated GPT/Claude/Ollama Cost | Costo Equivalente GPT/Claude/Ollama |

### Auditoría Operacional

| Antes | Después |
|-------|---------|
| Overview | Resumen General |
| Coverage Gaps | Brechas de Cobertura |
| Top Failures | Consultas No Resueltas Más Frecuentes |
| Top Routes | Canales Más Utilizados |
| Adoption | Adopción |

### Chat (modo técnico / depuración)

- Etiquetas: Canal, Tipo de consulta, Confianza, Modo, Intención detectada
- Valores API traducidos o ocultos (no se muestran `metadata`, `query_type` crudos)
- Modos: Determinístico / Generativo con IA

### Exportaciones

Archivos `brechas_cobertura.csv` / `.json` con columnas:

- Pregunta, Cantidad, Canal Utilizado
- Brecha de cobertura, Fecha de exportación

## Tooltips ejecutivos (ejemplos)

**Cobertura Operativa:** *Porcentaje de consultas resueltas mediante procesos empresariales estructurados.*

**Dependencia de IA Conversacional:** *Porcentaje de consultas que requirieron el canal conversacional general.*

## Validación automática

- `auditLocalizedCatalog()` — recorre el catálogo y detecta inglés prohibido
- `containsForbiddenEnglish()` — usado en pruebas de integración
- Patrones prohibidos: Overview, Top Queries, business_pipeline visible, etc.

```bash
cd frontend && npm test -- --run src/i18n
```

## Pruebas

| Suite | Cobertura |
|-------|-----------|
| `spanish.test.ts` | Traducciones, exportaciones, auditoría de catálogo |
| `spanishLocalization.integration.test.tsx` | Analytics + Audit sin inglés visible |
| `OperationalAuditPage.test.tsx` | Tablas, exportaciones localizadas |

### Página de Rendimiento

| Antes | Después |
|-------|---------|
| tokens | unidades de procesamiento |
| LLM / Human Language Layer / Intent Router | modelo de lenguaje / capa de lenguaje natural / enrutador de intención |
| Smart Savings / Traditional Architecture | Ahorro inteligente / Arquitectura tradicional |

Componentes actualizados: `SmartSavingsHero`, `CostOptimizationSection`, `ArchitecturalExplanation`, `ExecutiveSummarySection`, `PerformanceMetricsGrid`, `PerformanceHero`.

### Archivos clave

| Archivo | Rol |
|---------|-----|
| `frontend/src/i18n/spanish.ts` | Catálogo único + funciones de traducción y exportación |
| `frontend/src/i18n/spanish.test.ts` | Pruebas unitarias (≥90% cobertura) |
| `frontend/src/i18n/spanishLocalization.integration.test.tsx` | Integración Analytics + Audit |
| `docs/spanish_localization_v1.md` | Esta documentación |

## Texto residual en inglés (futuras versiones)

Elementos **intencionalmente** pendientes o de baja prioridad para usuarios de negocio:

| Área | Texto residual | Motivo |
|------|----------------|--------|
| Moneda | `USD` en costos equivalentes | Configuración financiera placeholder |
| Unidades | `ms`, `P50/P95/P99` | Convención técnica universal |
| Marcas | GPT, Claude, Ollama, Olnatura | Nombres de producto / marca |
| API interna | Claves JSON sin cambiar | Restricción: no modificar APIs |
| Código fuente | Identificadores TypeScript (`handled_by`, etc.) | No visibles al usuario |
| Logotipo alt | `Olnatura` | Nombre de marca |

## Restricciones respetadas

- Sin cambios en APIs REST
- Sin cambios en base de datos
- Sin cambios en observabilidad backend
- Sin cambios en lógica de negocio (pipeline, memory, fallback, etc.)
