import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { OperationalAuditPage } from '../pages/OperationalAuditPage'
import { es } from '../i18n/spanish'
import * as operationalAuditApi from '../services/operationalAuditApi'

vi.mock('../services/operationalAuditApi')

const mockData = {
  overview: {
    total_requests: 100,
    total_successes: 90,
    total_failures: 10,
    business_pipeline_pct: 50,
    memory_pct: 10,
    clarification_pct: 10,
    capability_pct: 10,
    fallback_pct: 10,
    legacy_pct: 10,
    coverage_score: 85,
    coverage_gap_score: 20,
  },
  coverageGaps: [
    { question: '¿Qué es un proveedor?', count: 5, route: 'legacy_chat' },
  ],
  topFailures: [{ question: 'fallo', route: 'legacy_chat', frequency: 2 }],
  topRoutes: [{ route: 'business_pipeline', count: 50, percentage: 50 }],
  adoption: {
    suggested_questions_usage: 30,
    conversation_memory_usage: 10,
    slot_clarification_usage: 10,
    capability_discovery_usage: 5,
  },
}

function mockExportCoverageGaps(format: 'json' | 'csv') {
  if (format === 'json') {
    return new Blob(
      [
        JSON.stringify({
          items: [{ question: 'x', count: 1, route: 'legacy_chat' }],
          coverage_gap_score: 10,
          exported_at: '2026-01-01',
        }),
      ],
      { type: 'application/json' },
    )
  }
  return new Blob(['question,count,route\nx,1,legacy_chat'], { type: 'text/csv' })
}

describe('OperationalAuditPage', () => {
  beforeEach(() => {
    vi.mocked(operationalAuditApi.getAuditOverview).mockResolvedValue(mockData.overview)
    vi.mocked(operationalAuditApi.getCoverageGaps).mockResolvedValue(mockData.coverageGaps)
    vi.mocked(operationalAuditApi.getTopFailures).mockResolvedValue(mockData.topFailures)
    vi.mocked(operationalAuditApi.getTopRoutes).mockResolvedValue(mockData.topRoutes)
    vi.mocked(operationalAuditApi.getAdoptionMetrics).mockResolvedValue(mockData.adoption)
    vi.mocked(operationalAuditApi.exportCoverageGaps).mockImplementation(async (format) =>
      mockExportCoverageGaps(format),
    )
    URL.createObjectURL = vi.fn(() => 'blob:mock')
    URL.revokeObjectURL = vi.fn()
  })

  it('renders overview cards and tables in Spanish', async () => {
    render(
      <MemoryRouter>
        <OperationalAuditPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByText(es.audit.eyebrow)).toBeInTheDocument()
    })
    expect(screen.getByText(es.audit.overview.title)).toBeInTheDocument()
    expect(screen.getByText(es.audit.coverageGaps.title)).toBeInTheDocument()
    expect(screen.getByText(es.audit.topFailures.title)).toBeInTheDocument()
    expect(screen.getByText(es.audit.topRoutes.title)).toBeInTheDocument()
    expect(screen.getByText(es.audit.adoption.title)).toBeInTheDocument()
    expect(screen.getAllByText('Conversación General').length).toBeGreaterThan(0)
  })

  it('exports coverage gaps as localized CSV', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <OperationalAuditPage />
      </MemoryRouter>,
    )

    const buttons = await screen.findAllByText(es.common.exportCsv)
    await user.click(buttons[0])
    expect(operationalAuditApi.exportCoverageGaps).toHaveBeenCalledWith('csv')
  })

  it('exports coverage gaps as localized JSON', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <OperationalAuditPage />
      </MemoryRouter>,
    )

    const buttons = await screen.findAllByText(es.common.exportJson)
    await user.click(buttons[0])
    expect(operationalAuditApi.exportCoverageGaps).toHaveBeenCalledWith('json')
  })
})
