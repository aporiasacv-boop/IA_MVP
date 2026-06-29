import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AnalyticsPage } from '../pages/AnalyticsPage'
import { OperationalAuditPage } from '../pages/OperationalAuditPage'
import { containsForbiddenEnglish, es } from '../i18n/spanish'
import * as businessAnalyticsApi from '../services/businessAnalyticsApi'
import * as operationalAuditApi from '../services/operationalAuditApi'

vi.mock('../services/businessAnalyticsApi')
vi.mock('../services/operationalAuditApi')

const mockAnalytics = {
  coverage: {
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
  },
  performance: {
    p50_ms: 10,
    p95_ms: 20,
    p99_ms: 30,
    avg_intent_ms: 1,
    avg_planner_ms: 1,
    avg_executor_ms: 1,
    avg_response_ms: 1,
    avg_total_ms: 15,
  },
  financial: {
    total_requests: 100,
    deterministic_requests: 80,
    ai_requests: 20,
    ai_avoidance_rate: 0.8,
    legacy_dependency_rate: 0.2,
    estimated_monthly_requests: 100,
    estimated_gpt_equivalent_calls: 20,
    estimated_claude_equivalent_calls: 20,
    estimated_ollama_calls: 20,
    estimated_gpt_cost: 0,
    estimated_claude_cost: 0,
    estimated_ollama_cost: 0,
  },
  topQueries: [
    {
      question: '¿Cuántos clientes existen?',
      count: 5,
      route: 'business_pipeline',
      success_rate: 1,
    },
  ],
  report: {
    coverage_score: 80,
    success_rate: 0.9,
    deterministic_rate: 0.8,
    legacy_rate: 0.1,
    top_routes: [],
  },
}

const mockAudit = {
  overview: {
    total_requests: 10,
    total_successes: 9,
    total_failures: 1,
    business_pipeline_pct: 50,
    memory_pct: 10,
    clarification_pct: 10,
    capability_pct: 10,
    fallback_pct: 10,
    legacy_pct: 10,
    coverage_score: 80,
    coverage_gap_score: 20,
  },
  coverageGaps: [
    { question: '¿Cómo van las ventas?', count: 2, route: 'guided_fallback' },
  ],
  topFailures: [{ question: 'fallo', route: 'legacy_chat', frequency: 1 }],
  topRoutes: [{ route: 'business_pipeline', count: 5, percentage: 50 }],
  adoption: {
    suggested_questions_usage: 3,
    conversation_memory_usage: 1,
    slot_clarification_usage: 1,
    capability_discovery_usage: 1,
  },
}

function assertNoForbiddenEnglish(container: HTMLElement) {
  const forbidden = containsForbiddenEnglish(container.textContent ?? '')
  expect(forbidden).toBeNull()
}

describe('Spanish localization integration', () => {
  beforeEach(() => {
    vi.mocked(businessAnalyticsApi.getCoverageAnalytics).mockResolvedValue(mockAnalytics.coverage)
    vi.mocked(businessAnalyticsApi.getPerformanceAnalytics).mockResolvedValue(
      mockAnalytics.performance,
    )
    vi.mocked(businessAnalyticsApi.getFinancialAnalytics).mockResolvedValue(mockAnalytics.financial)
    vi.mocked(businessAnalyticsApi.getTopQueriesAnalytics).mockResolvedValue(mockAnalytics.topQueries)
    vi.mocked(businessAnalyticsApi.getCoverageReport).mockResolvedValue(mockAnalytics.report)

    vi.mocked(operationalAuditApi.getAuditOverview).mockResolvedValue(mockAudit.overview)
    vi.mocked(operationalAuditApi.getCoverageGaps).mockResolvedValue(mockAudit.coverageGaps)
    vi.mocked(operationalAuditApi.getTopFailures).mockResolvedValue(mockAudit.topFailures)
    vi.mocked(operationalAuditApi.getTopRoutes).mockResolvedValue(mockAudit.topRoutes)
    vi.mocked(operationalAuditApi.getAdoptionMetrics).mockResolvedValue(mockAudit.adoption)
    vi.mocked(operationalAuditApi.exportCoverageGaps).mockImplementation(async (format) => {
      if (format === 'json') {
        return new Blob(
          [
            JSON.stringify({
              items: [{ question: 'x', count: 1, route: 'guided_fallback' }],
              coverage_gap_score: 10,
              exported_at: '2026-01-01',
            }),
          ],
          { type: 'application/json' },
        )
      }
      return new Blob(['question,count,route\nx,1,guided_fallback'], { type: 'text/csv' })
    })
    URL.createObjectURL = vi.fn(() => 'blob:mock')
    URL.revokeObjectURL = vi.fn()
  })

  it('renders Analytics page in Spanish without forbidden english', async () => {
    const { container } = render(
      <MemoryRouter>
        <AnalyticsPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByText(es.analytics.title)).toBeInTheDocument()
    })
    expect(screen.getByText(es.analytics.coverage.title)).toBeInTheDocument()
    expect(screen.getByText('Canal Empresarial')).toBeInTheDocument()
    assertNoForbiddenEnglish(container)
  })

  it('renders Operational Audit page in Spanish with localized exports', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <MemoryRouter>
        <OperationalAuditPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByText(es.audit.title)).toBeInTheDocument()
    })
    expect(screen.getByText(es.audit.coverageGaps.title)).toBeInTheDocument()
    expect(screen.getByText('Asistencia Guiada')).toBeInTheDocument()

    const exportButtons = screen.getAllByText(es.common.exportCsv)
    await user.click(exportButtons[0])
    expect(operationalAuditApi.exportCoverageGaps).toHaveBeenCalledWith('csv')

    assertNoForbiddenEnglish(container)
  })

  it('navigates between localized sections via router', async () => {
    const { unmount: unmountAnalytics } = render(
      <MemoryRouter initialEntries={['/analytics']}>
        <Routes>
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Routes>
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: es.analytics.title })).toBeInTheDocument()
    unmountAnalytics()

    render(
      <MemoryRouter initialEntries={['/audit']}>
        <Routes>
          <Route path="/audit" element={<OperationalAuditPage />} />
        </Routes>
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: es.audit.title })).toBeInTheDocument()
  })
})
