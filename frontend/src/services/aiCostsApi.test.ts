import { describe, expect, it, vi } from 'vitest'
import { getAICostSummary } from './aiCostsApi'

describe('aiCostsApi', () => {
  it('fetches cost summary', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          llm_requests: 2,
          provider_distribution: { mock: 2 },
          tokens_input: 100,
          tokens_output: 50,
          estimated_cost: 0,
          average_latency: 0.1,
          average_cost_per_question: 0,
          hallucination_guard_triggered: 0,
          llm_fallbacks: 0,
          cost_by_provider: [],
          daily_cost: 0,
          monthly_cost: 0,
          cost_per_user: {},
          cost_per_query: 0,
          provider_comparison: [],
        }),
      }),
    )
    const summary = await getAICostSummary()
    expect(summary.llm_requests).toBe(2)
    vi.unstubAllGlobals()
  })
})
