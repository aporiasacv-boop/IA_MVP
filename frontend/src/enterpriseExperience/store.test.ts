import { beforeEach, describe, expect, it } from 'vitest'
import { enterpriseExperienceStore, pathToScreen } from './store'

describe('enterpriseExperienceStore', () => {
  beforeEach(() => {
    enterpriseExperienceStore._resetForTests()
  })

  it('persiste contexto en sessionStorage', () => {
    enterpriseExperienceStore.setContext({ period: 'junio', scenario: 'produccion' })
    const context = enterpriseExperienceStore.getContext()
    expect(context.period).toBe('junio')
    expect(context.scenario).toBe('produccion')
  })

  it('registra telemetría de navegación', () => {
    enterpriseExperienceStore.recordNavigation({
      navigation_origin: 'executive_dashboard',
      navigation_target: 'enterprise_ai',
      deep_link_used: true,
      context_restored: true,
    })
    const event = enterpriseExperienceStore.getLastNavigation()
    expect(event?.navigation_origin).toBe('executive_dashboard')
    expect(event?.navigation_target).toBe('enterprise_ai')
    expect(event?.deep_link_used).toBe(true)
    expect(event?.context_restored).toBe(true)
  })

  it('deduplica consultas recientes', () => {
    enterpriseExperienceStore.addRecentQuery('Analiza ventas')
    enterpriseExperienceStore.addRecentQuery('Otra consulta')
    enterpriseExperienceStore.addRecentQuery('Analiza ventas')
    const recent = enterpriseExperienceStore.getSnapshot().recentQueries
    expect(recent).toHaveLength(2)
    expect(recent[0]?.question).toBe('Analiza ventas')
  })

  it('alterna consultas fijadas', () => {
    enterpriseExperienceStore.togglePin('Resume junio')
    expect(enterpriseExperienceStore.isPinned('Resume junio')).toBe(true)
    enterpriseExperienceStore.togglePin('Resume junio')
    expect(enterpriseExperienceStore.isPinned('Resume junio')).toBe(false)
  })
})

describe('pathToScreen', () => {
  it('mapea rutas principales a pantallas de experiencia', () => {
    expect(pathToScreen('/')).toBe('enterprise_ai')
    expect(pathToScreen('/dashboard')).toBe('executive_dashboard')
    expect(pathToScreen('/financiero')).toBe('financial_simulator')
  })
})
