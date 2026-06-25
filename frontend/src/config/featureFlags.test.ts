import { describe, expect, it } from 'vitest'
import { isDebugModeEnabled, isHybridChatEnabled } from './featureFlags'

describe('featureFlags', () => {
  describe('USE_HYBRID_CHAT', () => {
    it('habilita hybrid por defecto cuando la variable no está definida', () => {
      expect(isHybridChatEnabled(undefined)).toBe(true)
    })

    it('habilita hybrid cuando VITE_USE_HYBRID_CHAT=true', () => {
      expect(isHybridChatEnabled('true')).toBe(true)
    })

    it('deshabilita hybrid solo cuando VITE_USE_HYBRID_CHAT=false', () => {
      expect(isHybridChatEnabled('false')).toBe(false)
    })
  })

  describe('DEBUG_MODE', () => {
    it('deshabilita debug por defecto', () => {
      expect(isDebugModeEnabled(undefined)).toBe(false)
    })

    it('habilita debug solo con VITE_DEBUG_MODE=true', () => {
      expect(isDebugModeEnabled('true')).toBe(true)
      expect(isDebugModeEnabled('false')).toBe(false)
    })
  })
})
