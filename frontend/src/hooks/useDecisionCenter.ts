import { useCallback, useEffect, useState } from 'react'
import {
  getDecisionExample,
  getDecisionSchema,
  postDecisionRecommend,
  type DecisionRecommendRequest,
  type DecisionType,
  type EnterpriseDecisionPackage,
} from '../services/decisionApi'

const DECISION_LABELS: Record<DecisionType, string> = {
  proveedor_ia: 'Proveedor IA recomendado',
  escenario: 'Escenario recomendado',
  infraestructura: 'Infraestructura recomendada',
  estrategia_despliegue: 'Estrategia de despliegue',
  optimizacion_costos: 'Optimización de costos',
  optimizacion_ia: 'Optimización del uso de IA',
  optimizacion_pipeline: 'Optimización del Pipeline',
}

export function useDecisionCenter() {
  const [decisionTypes, setDecisionTypes] = useState<DecisionType[]>([])
  const [selectedType, setSelectedType] = useState<DecisionType>('proveedor_ia')
  const [scenarioId, setScenarioId] = useState('piloto')
  const [packageData, setPackageData] = useState<EnterpriseDecisionPackage | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadSchema = useCallback(async () => {
    const schema = await getDecisionSchema()
    const types = schema.decision_types as DecisionType[]
    setDecisionTypes(types)
  }, [])

  const loadExample = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const example = await getDecisionExample()
      setPackageData(example)
      setSelectedType(example.decision_type as DecisionType)
    } catch {
      setError('No fue posible cargar el ejemplo de decisión.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const recommend = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const payload: DecisionRecommendRequest = {
        decision_type: selectedType,
        scenario_id: scenarioId,
      }
      const result = await postDecisionRecommend(payload)
      setPackageData(result)
    } catch {
      setError('No fue posible generar la recomendación ejecutiva.')
    } finally {
      setIsLoading(false)
    }
  }, [scenarioId, selectedType])

  useEffect(() => {
    void loadSchema().catch(() => setError('No fue posible cargar el esquema de decisiones.'))
    void loadExample()
  }, [loadExample, loadSchema])

  return {
    decisionTypes,
    decisionLabels: DECISION_LABELS,
    selectedType,
    setSelectedType,
    scenarioId,
    setScenarioId,
    packageData,
    isLoading,
    error,
    recommend,
    refresh: loadExample,
  }
}
