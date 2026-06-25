import { useCallback, useEffect, useState } from 'react'
import * as operationalAuditApi from '../services/operationalAuditApi'
import type { OperationalAuditData } from '../types/operationalAudit'
import { es } from '../i18n/spanish'

export function useOperationalAudit() {
  const [data, setData] = useState<OperationalAuditData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [overview, coverageGaps, topFailures, topRoutes, adoption] = await Promise.all([
        operationalAuditApi.getAuditOverview(),
        operationalAuditApi.getCoverageGaps(50),
        operationalAuditApi.getTopFailures(50),
        operationalAuditApi.getTopRoutes(20),
        operationalAuditApi.getAdoptionMetrics(),
      ])
      setData({ overview, coverageGaps, topFailures, topRoutes, adoption })
    } catch {
      setError(es.common.errorAudit)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { data, isLoading, error, refresh }
}
