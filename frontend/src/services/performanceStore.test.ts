import { describe, expect, it } from 'vitest'
import { mapHybridToRecord } from './performanceStore'
import type { HybridChatResult } from '../types/hybrid-chat'

describe('performanceStore hybrid compatibility', () => {
  it('registra pipeline como determinístico', () => {
    const result: HybridChatResult = {
      handled_by: 'business_pipeline',
      success: true,
      answer: '50 clientes',
      metadata: { query_type: 'COUNT_CLIENTES', confidence: 1 },
    }

    const record = mapHybridToRecord('¿Cuántos clientes?', result)

    expect(record.response_mode).toBe('DETERMINISTIC')
    expect(record.intent).toBe('COUNT_CLIENTES')
  })

  it('registra legacy enrutado como generativo por defecto', () => {
    const result: HybridChatResult = {
      handled_by: 'legacy_chat',
      success: true,
      answer: 'Hola',
      metadata: { intent: 'GREETING', confidence: 0.9, response_mode: 'GENERATIVE' },
    }

    const record = mapHybridToRecord('Hola', result)

    expect(record.response_mode).toBe('GENERATIVE')
    expect(record.intent).toBe('GREETING')
  })
})
