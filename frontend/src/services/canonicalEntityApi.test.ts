import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getCanonicalStatistics } from './canonicalEntityApi'

describe('canonicalEntityApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('getCanonicalStatistics llama statistics', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          canonical_entities_total: 800,
          canonical_matches: 2,
          pending_matches: 15,
          automatic_suggestions: 40,
          commercial_entities_total: 800,
          resolved_entities: 800,
          unresolved_entities: 0,
          unresolved_pct: 0,
          orphan_entities: 0,
          last_suggestion_run: null,
        }),
      }),
    )
    const stats = await getCanonicalStatistics()
    expect(stats.canonical_entities_total).toBe(800)
    expect(stats.pending_matches).toBe(15)
  })
})
