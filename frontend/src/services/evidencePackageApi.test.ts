import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getEvidenceStatistics } from './evidencePackageApi'

describe('evidencePackageApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('getEvidenceStatistics', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          evidence_packages_total: 25,
          average_package_size: 4200,
          average_evidence_items: 12,
          average_confidence: 0.81,
          missing_evidence: 1,
          package_build_time: 0.05,
        }),
      }),
    )
    const stats = await getEvidenceStatistics()
    expect(stats.evidence_packages_total).toBe(25)
  })
})
