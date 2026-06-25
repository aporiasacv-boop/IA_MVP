import { useCallback, useEffect, useState } from 'react'
import * as semanticIntentApi from '../services/semanticIntentApi'
import type { BusinessExecutionPlan, SemanticParseResult, SemanticStatistics } from '../types/semanticIntent'

const SAMPLE_QUESTIONS = [
  'Listar los principales clientes con mayor volumen este mes',
  'Evaluar riesgos de la entidad WALMART',
  'Recomendar acciones para proveedores inactivos',
  '¿Quién es el cliente con más movimientos?',
]

export function useSemanticIntent() {
  const [question, setQuestion] = useState(SAMPLE_QUESTIONS[0])
  const [parse, setParse] = useState<SemanticParseResult | null>(null)
  const [plan, setPlan] = useState<BusinessExecutionPlan | null>(null)
  const [statistics, setStatistics] = useState<SemanticStatistics | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const analyze = useCallback(async (text: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const [parseResult, planResult, statsResult] = await Promise.all([
        semanticIntentApi.parseSemanticQuestion(text),
        semanticIntentApi.planSemanticExecution(text),
        semanticIntentApi.getSemanticStatistics(),
      ])
      setParse(parseResult)
      setPlan(planResult)
      setStatistics(statsResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void analyze(question)
  }, [])

  return {
    question,
    setQuestion,
    parse,
    plan,
    statistics,
    sampleQuestions: SAMPLE_QUESTIONS,
    isLoading,
    error,
    analyze,
  }
}
