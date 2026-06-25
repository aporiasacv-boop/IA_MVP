import { describe, expect, it } from 'vitest'
import type { CoverageAnalytics, FinancialAnalytics } from '../types/businessAnalytics'

describe('business analytics types', () => {
  it('coverage percentages can sum to 100', () => {
    const coverage: CoverageAnalytics = {
      total_requests: 100,
      business_pipeline: 50,
      slot_clarification: 10,
      conversation_memory: 10,
      capability_discovery: 10,
      guided_fallback: 10,
      legacy_chat: 10,
      business_pipeline_pct: 50,
      slot_clarification_pct: 10,
      conversation_memory_pct: 10,
      capability_discovery_pct: 10,
      guided_fallback_pct: 10,
      legacy_chat_pct: 10,
    }
    const sum =
      coverage.business_pipeline_pct +
      coverage.slot_clarification_pct +
      coverage.conversation_memory_pct +
      coverage.capability_discovery_pct +
      coverage.guided_fallback_pct +
      coverage.legacy_chat_pct
    expect(sum).toBe(100)
  })

  it('financial avoidance and legacy rates are complementary', () => {
    const financial: FinancialAnalytics = {
      total_requests: 100,
      deterministic_requests: 80,
      ai_requests: 20,
      ai_avoidance_rate: 0.8,
      legacy_dependency_rate: 0.2,
      estimated_monthly_requests: 80,
      estimated_gpt_equivalent_calls: 20,
      estimated_claude_equivalent_calls: 20,
      estimated_ollama_calls: 20,
      estimated_gpt_cost: 0,
      estimated_claude_cost: 0,
      estimated_ollama_cost: 0,
    }
    expect(financial.ai_avoidance_rate + financial.legacy_dependency_rate).toBe(1)
  })
})
