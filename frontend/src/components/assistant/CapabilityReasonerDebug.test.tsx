import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { CapabilityReasonerDebug } from './CapabilityReasonerDebug'
import type { ChatMessage } from '../../types/chat'

const message: ChatMessage = {
  id: 'a-2',
  role: 'assistant',
  content: 'Respuesta.',
  hybrid: {
    handledBy: 'guided_fallback',
    rawMetadata: {
      reasoning_goal: 'Analizar clientes',
      estimated_coverage: 85,
      recommended_plan:
        'Con las capacidades existentes puedo cubrir aproximadamente el 85% de la intención.',
      capability_reasoner_plan: {
        reasoning_goal: 'Analizar clientes',
        estimated_coverage: 85,
        candidate_capabilities: [
          { capability_id: 'TOP_CLIENTES', score: 0.82 },
          { capability_id: 'KPIS', score: 0.71 },
        ],
        selected_capabilities: ['TOP_CLIENTES', 'KPIS'],
        recommended_plan:
          'Recomiendo responder utilizando TOP_CLIENTES y complementar posteriormente con KPIS.',
        fallback_recommended: false,
      },
    },
  },
}

describe('CapabilityReasonerDebug', () => {
  it('muestra el plan recomendado en modo debug', () => {
    render(<CapabilityReasonerDebug message={message} />)

    expect(screen.getByText('Capability Reasoner')).toBeInTheDocument()
    expect(screen.getByText('Analizar clientes')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('TOP_CLIENTES — score: 0.82')).toBeInTheDocument()
    expect(screen.getByText(/complementar posteriormente con KPIS/)).toBeInTheDocument()
  })
})
