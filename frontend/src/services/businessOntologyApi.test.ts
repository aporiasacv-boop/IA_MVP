import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getOntologyStatistics } from './businessOntologyApi'

describe('businessOntologyApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('getOntologyStatistics', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          ontology_entities: 100,
          ontology_pending: 80,
          ontology_approved: 5,
          ontology_rejected: 2,
          ontology_rules: 25,
          ontology_types: 35,
          ontology_average_confidence: 0.82,
          entities_without_suggestions: 10,
        }),
      }),
    )
    const stats = await getOntologyStatistics()
    expect(stats.ontology_pending).toBe(80)
  })
})
