import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getKnowledgeStatistics } from './enterpriseKnowledgeApi'

describe('enterpriseKnowledgeApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('getKnowledgeStatistics', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          knowledge_objects_total: 50,
          canonical_entities_total: 60,
          knowledge_build_time: 2.5,
          knowledge_average_completeness: 0.75,
          knowledge_average_confidence: 0.8,
          incomplete_objects: 3,
        }),
      }),
    )
    const stats = await getKnowledgeStatistics()
    expect(stats.knowledge_objects_total).toBe(50)
  })
})
