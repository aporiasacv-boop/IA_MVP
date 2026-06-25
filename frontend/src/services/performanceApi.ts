import { sendChatQuestion, isHybridChatResult } from './chatApi'
import { mapHybridToRecord, mapResponseToRecord, mergeRecords } from './performanceStore'
import type { PerformanceRecord } from '../types/performance'

const BENCHMARK_QUESTIONS = [
  'Hola',
  '¿Quién eres?',
  '¿Qué KPIs tienes?',
  '¿Quién es nuestro mejor cliente?',
  '¿Qué pasó en junio?',
  '¿Qué insights detectaste?',
]

const CACHE_KEY = 'ia_mvp_benchmark_cache'
const CACHE_TTL_MS = 10 * 60 * 1000

interface BenchmarkCache {
  recorded_at: string
  records: PerformanceRecord[]
}

export async function runPerformanceBenchmark(): Promise<PerformanceRecord[]> {
  const cached = readBenchmarkCache()
  if (cached) return cached

  const records: PerformanceRecord[] = []
  for (const question of BENCHMARK_QUESTIONS) {
    const response = await sendChatQuestion(question)
    records.push(
      isHybridChatResult(response)
        ? mapHybridToRecord(question, response)
        : mapResponseToRecord(question, response),
    )
  }

  writeBenchmarkCache(records)
  return records
}

export async function loadLivePerformanceRecords(
  sessionRecords: PerformanceRecord[],
): Promise<PerformanceRecord[]> {
  const benchmarkRecords = await runPerformanceBenchmark()
  return mergeRecords(sessionRecords, benchmarkRecords)
}

function readBenchmarkCache(): PerformanceRecord[] | null {
  try {
    const raw = sessionStorage.getItem(CACHE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as BenchmarkCache
    const age = Date.now() - new Date(parsed.recorded_at).getTime()
    if (age > CACHE_TTL_MS) return null
    return parsed.records
  } catch {
    return null
  }
}

function writeBenchmarkCache(records: PerformanceRecord[]): void {
  const payload: BenchmarkCache = {
    recorded_at: new Date().toISOString(),
    records,
  }
  sessionStorage.setItem(CACHE_KEY, JSON.stringify(payload))
}
