import { useCallback, useEffect, useState } from 'react'
import * as evidencePackageApi from '../services/evidencePackageApi'
import type { EnterpriseEvidencePackage, EvidenceStatistics } from '../types/evidencePackage'

const SAMPLES = [
  'Evaluar riesgos del cliente con mayor volumen',
  'Recomendar acciones para proveedores inactivos',
  'Listar clientes principales este mes',
]

export function useEvidencePackage() {
  const [question, setQuestion] = useState(SAMPLES[0])
  const [package_, setPackage] = useState<EnterpriseEvidencePackage | null>(null)
  const [statistics, setStatistics] = useState<EvidenceStatistics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const build = useCallback(async (text: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const [pkg, stats] = await Promise.all([
        evidencePackageApi.buildEvidencePackage(text),
        evidencePackageApi.getEvidenceStatistics(),
      ])
      setPackage(pkg)
      setStatistics(stats)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const loadExample = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [pkg, stats] = await Promise.all([
        evidencePackageApi.getEvidenceExample(),
        evidencePackageApi.getEvidenceStatistics(),
      ])
      setPackage(pkg)
      setStatistics(stats)
      setQuestion(pkg.question)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadExample()
  }, [loadExample])

  return {
    question,
    setQuestion,
    package: package_,
    statistics,
    samples: SAMPLES,
    isLoading,
    error,
    build,
    loadExample,
  }
}
