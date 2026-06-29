import { useCallback, useEffect, useState } from 'react'

import { es } from '../i18n/spanish'
import {
  agendaFromHybridMetadata,
  fetchExecutiveAgenda,
  type ExecutiveAgendaParams,
  type ExecutiveAgendaResponse,
} from '../services/executiveAdvisorApi'

export function useExecutiveAdvisor(params: ExecutiveAgendaParams) {
  const [data, setData] = useState<ExecutiveAgendaResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [updatedFromConversation, setUpdatedFromConversation] = useState(false)

  const loadInitial = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const agenda = await fetchExecutiveAgenda(params)
      setData(agenda)
      setUpdatedFromConversation(false)
    } catch {
      setError(es.executiveAdvisor.loadError)
    } finally {
      setIsLoading(false)
    }
  }, [params.period, params.scenario, params.sessionId])

  useEffect(() => {
    void loadInitial()
  }, [loadInitial])

  const applyFromHybridMetadata = useCallback((metadata: Record<string, unknown>) => {
    const agenda = agendaFromHybridMetadata(metadata)
    if (!agenda) return
    setData(agenda)
    setUpdatedFromConversation(true)
    setError(null)
  }, [])

  return {
    data,
    isLoading,
    error,
    updatedFromConversation,
    applyFromHybridMetadata,
    refresh: loadInitial,
  }
}
