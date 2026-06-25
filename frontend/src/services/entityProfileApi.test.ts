import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getEntityProfileStatistics } from './entityProfileApi'

describe('entityProfileApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('getEntityProfileStatistics llama statistics', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          entity_profiles_total: 800,
          canonical_entities_total: 800,
          profiles_without_movements: 10,
          average_profile_completeness: 0.72,
          profile_generation_time: 4.2,
          last_profile_refresh: null,
          total_movements_profiled: 50000,
          average_movements_per_profile: 62.5,
        }),
      }),
    )
    const stats = await getEntityProfileStatistics()
    expect(stats.entity_profiles_total).toBe(800)
    expect(stats.average_profile_completeness).toBe(0.72)
  })
})
