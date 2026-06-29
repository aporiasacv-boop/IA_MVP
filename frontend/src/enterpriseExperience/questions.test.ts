import { describe, expect, it } from 'vitest'
import {
  buildContextualSuggestions,
  buildFinancialQuestion,
  buildKpiQuestion,
} from './questions'

describe('buildKpiQuestion', () => {
  it('genera pregunta sin periodo cuando no hay contexto temporal', () => {
    const question = buildKpiQuestion('clients', null)
    expect(question).toContain('clientes registrados')
    expect(question).not.toContain('periodo')
  })

  it('incorpora periodo sin copiar números del KPI', () => {
    const question = buildKpiQuestion('activity', 'junio')
    expect(question).toContain('junio')
    expect(question).not.toMatch(/\d/)
  })
})

describe('buildFinancialQuestion', () => {
  it('genera pregunta explicativa para costo mensual', () => {
    const question = buildFinancialQuestion('monthly_cost', null)
    expect(question).toContain('costo mensual')
    expect(question).not.toMatch(/\$\d/)
  })

  it('incorpora escenario seleccionado', () => {
    const question = buildFinancialQuestion('monthly_cost', 'produccion')
    expect(question).toContain('produccion')
  })
})

describe('buildContextualSuggestions', () => {
  it('prioriza sugerencias del dashboard cuando lastScreen es executive_dashboard', () => {
    const suggestions = buildContextualSuggestions({
      period: 'junio',
      scenario: null,
      lastScreen: 'executive_dashboard',
    })
    expect(suggestions.some((s) => s.includes('junio'))).toBe(true)
    expect(suggestions.some((s) => s.includes('clientes'))).toBe(true)
  })

  it('prioriza sugerencias financieras cuando lastScreen es financial_simulator', () => {
    const suggestions = buildContextualSuggestions({
      period: null,
      scenario: 'produccion',
      lastScreen: 'financial_simulator',
    })
    expect(suggestions.some((s) => s.includes('costos'))).toBe(true)
    expect(suggestions.some((s) => s.includes('produccion'))).toBe(true)
  })
})
