import type { ChatApiResponse } from '../types/chat'
import type { HybridChatResult } from '../types/hybrid-chat'
import type { PerformanceMetrics, PerformanceRecord, SavingsExample } from '../types/performance'

const STORAGE_KEY = 'ia_mvp_performance_records'
const MAX_RECORDS = 500
const TOKEN_COST_USD = 0.002

const PREFERRED_SAVINGS_QUESTIONS = [
  '¿Qué KPIs tienes?',
  '¿Quién es nuestro mejor cliente?',
  '¿Qué pasó en junio?',
]

export function recordChatResponse(question: string, response: ChatApiResponse): void {
  const records = getPerformanceRecords()
  records.push(mapResponseToRecord(question, response))
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records.slice(-MAX_RECORDS)))
}

export function recordHybridResponse(question: string, response: HybridChatResult): void {
  const records = getPerformanceRecords()
  records.push(mapHybridToRecord(question, response))
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records.slice(-MAX_RECORDS)))
}

export function mapHybridToRecord(question: string, response: HybridChatResult): PerformanceRecord {
  const isPipeline = response.handled_by === 'business_pipeline'
  const legacyMode = response.metadata.response_mode
  const responseMode =
    isPipeline
      ? 'DETERMINISTIC'
      : legacyMode === 'DETERMINISTIC' || legacyMode === 'GENERATIVE'
        ? legacyMode
        : 'GENERATIVE'

  const intent =
    typeof response.metadata.query_type === 'string'
      ? response.metadata.query_type
      : typeof response.metadata.intent === 'string'
        ? response.metadata.intent
        : response.handled_by

  return {
    question,
    response_mode: responseMode,
    total_ms: 0,
    llm_ms: 0,
    estimated_tokens: 0,
    intent,
    recorded_at: new Date().toISOString(),
  }
}

export function getPerformanceRecords(): PerformanceRecord[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as PerformanceRecord[]
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function mapResponseToRecord(
  question: string,
  response: ChatApiResponse,
): PerformanceRecord {
  return {
    question,
    response_mode: response.response_mode,
    total_ms: response.timings.total_ms,
    llm_ms: response.timings.llm_ms,
    estimated_tokens: response.prompt_metrics?.estimated_tokens ?? 0,
    intent: response.intent,
    recorded_at: new Date().toISOString(),
  }
}

export function estimateTraditionalTokens(question: string): number {
  return Math.max(650, Math.round(question.length * 12 + 400))
}

export function estimateTraditionalTimeMs(record: PerformanceRecord): number {
  if (record.response_mode === 'GENERATIVE' && record.llm_ms > 0) {
    return Math.max(record.llm_ms, 3500)
  }
  return 4200
}

export function aggregateRecords(records: PerformanceRecord[]): PerformanceMetrics {
  if (records.length === 0) {
    return {
      totalQueries: 0,
      deterministicQueries: 0,
      generativeQueries: 0,
      averageResponseMs: 0,
      tokensSaved: 0,
      estimatedCostAvoidedUsd: 0,
      llmCallsAvoided: 0,
    }
  }

  const deterministicQueries = records.filter((r) => r.response_mode === 'DETERMINISTIC').length
  const generativeQueries = records.length - deterministicQueries
  const averageResponseMs =
    records.reduce((sum, r) => sum + r.total_ms, 0) / records.length

  let tokensSaved = 0
  for (const record of records) {
    const traditional = estimateTraditionalTokens(record.question)
    const actual = record.estimated_tokens
    tokensSaved += Math.max(0, traditional - actual)
  }

  return {
    totalQueries: records.length,
    deterministicQueries,
    generativeQueries,
    averageResponseMs,
    tokensSaved,
    estimatedCostAvoidedUsd: tokensSaved * TOKEN_COST_USD,
    llmCallsAvoided: deterministicQueries,
  }
}

export function pickSavingsExample(records: PerformanceRecord[]): SavingsExample | null {
  if (records.length === 0) return null

  const preferred = records.find((r) =>
    PREFERRED_SAVINGS_QUESTIONS.some((q) => q.toLowerCase() === r.question.toLowerCase()),
  )
  const candidate =
    preferred ??
    records.find((r) => r.response_mode === 'DETERMINISTIC') ??
    records[0]

  const traditionalTokens = estimateTraditionalTokens(candidate.question)
  const actualTokens = candidate.estimated_tokens
  const savingsPercent =
    traditionalTokens === 0
      ? 0
      : Math.round(((traditionalTokens - actualTokens) / traditionalTokens) * 100)

  return {
    question: candidate.question,
    traditionalTokens,
    actualTokens,
    savingsPercent: Math.max(0, savingsPercent),
    traditionalTimeMs: estimateTraditionalTimeMs(candidate),
    actualTimeMs: Math.round(candidate.total_ms),
  }
}

export function mergeRecords(
  sessionRecords: PerformanceRecord[],
  benchmarkRecords: PerformanceRecord[],
): PerformanceRecord[] {
  const seen = new Set(sessionRecords.map((r) => `${r.question}|${r.recorded_at}`))
  const merged = [...sessionRecords]
  for (const record of benchmarkRecords) {
    const key = `${record.question}|${record.recorded_at}`
    if (!seen.has(key)) {
      merged.push(record)
      seen.add(key)
    }
  }
  return merged
}
