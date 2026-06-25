import { describe, expect, it } from 'vitest'
import {
  HANDLED_BY_LABELS,
  METRIC_TOOLTIPS,
  auditLocalizedCatalog,
  containsForbiddenEnglish,
  es,
  localizeCoverageGapsCsv,
  localizeCoverageGapsJson,
  formatProcessingUnits,
  translateDomain,
  translateHandledBy,
  translateQueryType,
  translateResponseMode,
  getMetricTooltip,
  collectLocalizedUiStrings,
} from './spanish'

describe('spanish localization catalog', () => {
  it('translates handled_by values for business users', () => {
    expect(translateHandledBy('business_pipeline')).toBe('Canal Empresarial')
    expect(translateHandledBy('conversation_memory')).toBe('Memoria Conversacional')
    expect(translateHandledBy('slot_clarification')).toBe('Aclaración de Consulta')
    expect(translateHandledBy('guided_fallback')).toBe('Asistencia Guiada')
    expect(translateHandledBy('capability_discovery')).toBe('Descubrimiento de Capacidades')
    expect(translateHandledBy('legacy_chat')).toBe('Conversación General')
    expect(translateHandledBy(null)).toBe('—')
    expect(translateHandledBy('unknown_route')).toBe('unknown_route')
  })

  it('translates analytics metric labels via es catalog', () => {
    expect(es.audit.overview.coverageScore).toBe('Cobertura operativa')
    expect(es.audit.overview.coverageGapScore).toBe('Brecha de cobertura')
    expect(es.analytics.topQueries.successRate).toBe('Tasa de éxito')
    expect(es.analytics.performance.avgTotalTime).toBe('Tiempo promedio de respuesta')
    expect(es.analytics.topQueries.title).toBe('Consultas más frecuentes')
    expect(es.performance.topDomains).toBe('Dominios más consultados')
  })

  it('translates financial metrics labels', () => {
    expect(es.analytics.financial.aiAvoidanceRate).toBe('Consultas resueltas sin IA')
    expect(es.analytics.financial.legacyDependencyRate).toBe('Dependencia de IA conversacional')
    expect(es.analytics.financial.gptCost).toBe('Costo equivalente GPT')
    expect(es.analytics.financial.claudeCost).toBe('Costo equivalente Claude')
    expect(es.analytics.financial.ollamaCost).toBe('Costo equivalente Ollama')
  })

  it('translates operational audit sections', () => {
    expect(es.audit.coverageGaps.title).toBe('Brechas de cobertura')
    expect(es.audit.topFailures.title).toBe('Consultas no resueltas más frecuentes')
    expect(es.audit.topRoutes.title).toBe('Canales más utilizados')
    expect(es.audit.adoption.title).toBe('Adopción')
    expect(es.audit.overview.title).toBe('Resumen general')
  })

  it('provides executive tooltips for key metrics', () => {
    expect(METRIC_TOOLTIPS.coverageScore).toContain('procesos empresariales')
    expect(METRIC_TOOLTIPS.legacyDependencyRate).toContain('canal conversacional general')
  })

  it('translates query types and response modes for chat', () => {
    expect(translateQueryType('COUNT_CLIENTES')).toBe('Conteo de clientes')
    expect(translateQueryType('UNKNOWN_TYPE')).toBe('unknown type')
    expect(translateQueryType(undefined)).toBe('—')
    expect(translateResponseMode('DETERMINISTIC')).toBe('Determinístico')
    expect(translateResponseMode('CUSTOM')).toBe('CUSTOM')
    expect(translateResponseMode(null)).toBe('—')
    expect(translateDomain('VENTAS')).toBe('Ventas')
    expect(translateDomain('OTRO')).toBe('OTRO')
    expect(translateDomain(undefined)).toBe('—')
    expect(getMetricTooltip('coverageScore')).toContain('procesos empresariales')
  })

  it('localizes coverage gaps csv export', () => {
    const csv = 'question,count,route\n¿Ventas?,3,guided_fallback'
    const localized = localizeCoverageGapsCsv(csv)
    expect(localized).toContain('Pregunta')
    expect(localized).toContain('Canal Utilizado')
    expect(localized).toContain('Asistencia Guiada')
    expect(localized).not.toContain('guided_fallback')
    expect(localizeCoverageGapsCsv('')).toBe('')
    expect(localizeCoverageGapsCsv('question,count\nsolo,dos')).toContain('Pregunta')
  })

  it('localizes coverage gaps json export with partial payloads', () => {
    const json = JSON.stringify({
      items: [{ question: '¿Ventas?', count: 2, route: 'legacy_chat' }],
      coverage_gap_score: 10,
      exported_at: '2026-01-01',
    })
    const localized = localizeCoverageGapsJson(json)
    expect(localized).toContain('Brecha de cobertura')
    expect(localized).toContain('Conversación General')
    expect(localized).not.toContain('coverage_gap_score')
    expect(localized).not.toContain('legacy_chat')
    expect(localizeCoverageGapsJson('{}')).toBe('{}')
  })

  it('collects localized strings for audit traversal', () => {
    const strings = collectLocalizedUiStrings()
    expect(strings.length).toBeGreaterThan(50)
    expect(strings).toContain(es.audit.title)
  })

  it('catalog audit finds no forbidden english in localized strings', () => {
    expect(auditLocalizedCatalog()).toEqual([])
  })

  it('reports injected forbidden strings during audit', () => {
    const violations = auditLocalizedCatalog(['Top Queries'])
    expect(violations[0]).toContain('Top Queries')
  })

  it('detects forbidden english patterns', () => {
    expect(containsForbiddenEnglish('Top Queries')).toBe('Top Queries')
    expect(containsForbiddenEnglish('Cobertura operativa')).toBeNull()
  })

  it('formats processing units for performance comparisons', () => {
    expect(formatProcessingUnits(0)).toContain('unidades de procesamiento')
    expect(formatProcessingUnits(500)).toContain('~500')
    expect(formatProcessingUnits(1500)).toContain('~1.5k')
  })

  it('covers all handled_by keys', () => {
    expect(Object.keys(HANDLED_BY_LABELS)).toHaveLength(6)
  })
})
