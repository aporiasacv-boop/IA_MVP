import { useCallback, useEffect, useState } from 'react'
import {
  getSimulationRecommendations,
  getSimulationScenarios,
  runSimulation,
  type PredefinedScenario,
  type SimulationRecommendation,
  type SimulationRunResponse,
  type SimulationScenarioInput,
} from '../services/simulationApi'

const DEFAULT_SCENARIO: SimulationScenarioInput = {
  scenario_id: 'custom',
  name: 'Hipótesis Personalizada',
  users: 100,
  queries_per_user_day: 12,
  business_pipeline_pct: 40,
  knowledge_service_pct: 25,
  conversation_memory_pct: 10,
  executive_reasoning_pct: 5,
  legacy_chat_pct: 10,
  llm_provider: 'openai',
  concurrency: 10,
  peak_hours: 8,
  working_days: 22,
}

export function useSimulator() {
  const [predefined, setPredefined] = useState<PredefinedScenario[]>([])
  const [scenario, setScenario] = useState<SimulationScenarioInput>(DEFAULT_SCENARIO)
  const [result, setResult] = useState<SimulationRunResponse | null>(null)
  const [recommendations, setRecommendations] = useState<SimulationRecommendation[]>([])
  const [baselineSource, setBaselineSource] = useState('defaults')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadScenarios = useCallback(async () => {
    const data = await getSimulationScenarios()
    setPredefined(data.predefined)
    setBaselineSource(data.baseline.source)
  }, [])

  const run = useCallback(async (input?: SimulationScenarioInput) => {
    setIsLoading(true)
    setError(null)
    try {
      const payload = input ?? scenario
      const runResult = await runSimulation(payload)
      setResult(runResult)
      const recs = await getSimulationRecommendations()
      setRecommendations(recs.recommendations)
    } catch {
      setError('No fue posible ejecutar la simulación.')
    } finally {
      setIsLoading(false)
    }
  }, [scenario])

  const applyPredefined = useCallback((id: string) => {
    const item = predefined.find((entry) => entry.id === id)
    if (!item) return
    setScenario(item.defaults)
    void run(item.defaults)
  }, [predefined, run])

  useEffect(() => {
    void loadScenarios().catch(() => setError('No fue posible cargar escenarios.'))
  }, [loadScenarios])

  return {
    predefined,
    scenario,
    setScenario,
    result,
    recommendations,
    baselineSource,
    isLoading,
    error,
    run,
    applyPredefined,
  }
}
