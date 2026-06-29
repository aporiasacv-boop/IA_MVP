import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ExecutiveInsightPanel } from './ExecutiveInsightPanel'
import type { ChatMessage } from '../../types/chat'

function buildMessage(insight: Record<string, unknown> | undefined): ChatMessage {
  return {
    id: '1',
    role: 'assistant',
    content: 'Existen 48 clientes activos.',
    timestamp: new Date(),
    hybrid: {
      handledBy: 'business_pipeline',
      queryType: 'COUNT_CLIENTES',
      success: true,
      rawMetadata: insight
        ? { executive_insight: insight, insight_source: insight.source ?? 'executive_insight' }
        : {},
    },
  }
}

describe('ExecutiveInsightPanel', () => {
  it('muestra bloques con evidencia y oculta secciones vacías', () => {
    render(
      <ExecutiveInsightPanel
        message={buildMessage({
          executive_summary: 'La base mantiene 48 clientes activos.',
          business_interpretation: 'La cartera es acotada y concentrada.',
          findings: ['El ranking concentra actividad en pocos clientes.'],
          possible_risks: [],
          recommendations: ['Revisar concentración por cliente.'],
          source: 'executive_reasoning_v2',
        })}
      />,
    )

    expect(screen.getByText('Análisis IA')).toBeInTheDocument()
    expect(screen.getByText('Resumen Ejecutivo')).toBeInTheDocument()
    expect(screen.getByText('Hallazgos')).toBeInTheDocument()
    expect(screen.getByText('Interpretación')).toBeInTheDocument()
    expect(screen.queryByText('Riesgos Potenciales')).not.toBeInTheDocument()
    expect(screen.getByText('Recomendaciones')).toBeInTheDocument()
    expect(screen.getByText('Revisar concentración por cliente.')).toBeInTheDocument()
  })

  it('no renderiza nada si no hay insight', () => {
    const { container } = render(<ExecutiveInsightPanel message={buildMessage(undefined)} />)
    expect(container).toBeEmptyDOMElement()
  })
})
