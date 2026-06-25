import { describe, expect, it } from 'vitest'
import type { MetricsSummary, PerformanceStats, TopQueryItem } from './metrics'

describe('metrics types', () => {
  it('acepta respuesta de summary del backend', () => {
    const summary: MetricsSummary = {
      total_requests: 100,
      business_pipeline_requests: 72,
      legacy_chat_requests: 28,
      avg_total_time_ms: 85.3,
      avg_database_time_ms: 22.1,
      avg_ollama_time_ms: 1800,
    }

    expect(summary.total_requests).toBe(100)
    expect(summary.business_pipeline_requests + summary.legacy_chat_requests).toBe(100)
  })

  it('acepta percentiles de performance', () => {
    const stats: PerformanceStats = {
      p50_total_time_ms: 40,
      p95_total_time_ms: 120,
      p99_total_time_ms: 250,
      averages: { total_time_ms: 55 },
    }

    expect(stats.p50_total_time_ms).toBeLessThan(stats.p95_total_time_ms)
  })

  it('acepta top queries', () => {
    const items: TopQueryItem[] = [
      { question: '¿Cuántos clientes?', count: 12 },
    ]

    expect(items[0].count).toBe(12)
  })
})
