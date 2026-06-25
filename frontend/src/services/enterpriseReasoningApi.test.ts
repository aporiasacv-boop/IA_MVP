import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getReasoningStatistics } from './enterpriseReasoningApi'

describe('enterpriseReasoningApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('getReasoningStatistics', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          reasoning_objects_total: 40,
          knowledge_objects_total: 50,
          reasoning_rules_executed: 720,
          average_reasoning_confidence: 0.82,
          average_findings: 1.5,
          average_alerts: 0.8,
          average_recommendations: 1.2,
          incomplete_objects: 2,
        }),
      }),
    )
    const stats = await getReasoningStatistics()
    expect(stats.reasoning_objects_total).toBe(40)
  })
})
