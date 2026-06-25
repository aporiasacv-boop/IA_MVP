import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getSemanticStatistics } from './semanticIntentApi'

describe('semanticIntentApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('getSemanticStatistics', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          semantic_parses: 100,
          execution_plans: 80,
          verb_distribution: { listar: 30 },
          average_semantic_confidence: 0.78,
          planner_success_rate: 0.85,
          unknown_verbs: 5,
        }),
      }),
    )
    const stats = await getSemanticStatistics()
    expect(stats.semantic_parses).toBe(100)
  })
})
