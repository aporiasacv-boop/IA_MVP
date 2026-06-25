import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getBusinessEntityStatistics, listBusinessEntities } from './businessEntityApi'

describe('businessEntityApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('listBusinessEntities construye query params', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    await listBusinessEntities({
      search: 'nomina',
      source_column: 'cuenta_proveedor',
      page: 2,
      page_size: 10,
    })

    const [url] = fetchMock.mock.calls[0] as [string]
    expect(url).toContain('search=nomina')
    expect(url).toContain('source_column=cuenta_proveedor')
    expect(url).toContain('page=2')
  })

  it('getBusinessEntityStatistics llama statistics', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          business_entities_total: 100,
          business_entities_loaded: 50,
          duplicated_entities: 3,
          last_entity_refresh: null,
          by_source_column: {},
          by_classification_status: {},
        }),
      }),
    )

    const stats = await getBusinessEntityStatistics()
    expect(stats.business_entities_total).toBe(100)
  })
})
