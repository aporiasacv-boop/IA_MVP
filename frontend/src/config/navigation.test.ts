import { describe, expect, it } from 'vitest'
import { DEBUG_NAV, EXECUTIVE_NAV } from './navigation'
import { es } from '../i18n/spanish'

describe('executive navigation', () => {
  it('expone tres rutas principales para usuarios ejecutivos', () => {
    expect(EXECUTIVE_NAV).toHaveLength(3)
    expect(EXECUTIVE_NAV.map((item) => item.to)).toEqual(['/', '/dashboard', '/financiero'])
    expect(EXECUTIVE_NAV[0]?.label).toBe(es.nav.enterpriseAi)
    expect(EXECUTIVE_NAV[1]?.label).toBe(es.nav.executiveDashboard)
    expect(EXECUTIVE_NAV[2]?.label).toBe(es.nav.financialSimulator)
  })

  it('mantiene herramientas técnicas bajo prefijo debug', () => {
    expect(DEBUG_NAV.length).toBeGreaterThan(10)
    expect(DEBUG_NAV.every((item) => item.to.startsWith('/debug/'))).toBe(true)
  })
})
