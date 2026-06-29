import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getEnterpriseKnowledgeStatistics } from './enterpriseKnowledgeApi'

describe('enterpriseKnowledgeApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('getEnterpriseKnowledgeStatistics', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          total_documents: 50,
          documents_by_category: { faq: 10 },
          faq_entries: 10,
          knowledge_requests: 100,
          knowledge_runtime_hits: 80,
          knowledge_runtime_misses: 20,
          knowledge_runtime_cache_hits: 75,
          knowledge_runtime_reload_time_ms: 12.5,
          knowledge_runtime_last_refresh: '2026-01-01T00:00:00Z',
          provider_distribution: { local: 50 },
          cache_hit_rate: 0.8,
          cache_size: 50,
          average_search_time_ms: 3.2,
          knowledge_sources: ['local'],
        }),
      }),
    )
    const stats = await getEnterpriseKnowledgeStatistics()
    expect(stats.total_documents).toBe(50)
  })
})
