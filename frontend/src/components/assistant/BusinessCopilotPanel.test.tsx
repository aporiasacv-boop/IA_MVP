import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { BusinessCopilotPanel } from './BusinessCopilotPanel'
import type { ChatMessage } from '../../types/chat'

function buildMessage(proposals: Record<string, unknown>[] | undefined): ChatMessage {
  return {
    id: '1',
    role: 'assistant',
    content: 'Respuesta empresarial',
    timestamp: new Date(),
    hybrid: {
      handledBy: 'business_pipeline',
      queryType: 'TOP_CLIENTES',
      success: true,
      rawMetadata: proposals ? { business_copilot_proposals: proposals } : {},
    },
  }
}

describe('BusinessCopilotPanel', () => {
  it('renderiza tarjetas y dispara la consulta al hacer clic', async () => {
    const onSelect = vi.fn()
    const user = userEvent.setup()

    render(
      <BusinessCopilotPanel
        message={buildMessage([
          {
            title: 'Analizar concentración comercial',
            rationale: 'Los primeros clientes concentran actividad.',
            action_label: 'Analizar',
            query: '¿Qué porcentaje representan los primeros cinco clientes?',
            proposal_type: 'profundizar',
          },
        ])}
        onSelectProposal={onSelect}
      />,
    )

    expect(screen.getByText('Próximos análisis sugeridos')).toBeInTheDocument()
    expect(screen.getByText('Analizar concentración comercial')).toBeInTheDocument()
    expect(screen.getByText('¿Por qué?')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Analizar' }))
    expect(onSelect).toHaveBeenCalledWith(
      '¿Qué porcentaje representan los primeros cinco clientes?',
    )
  })

  it('no renderiza nada sin propuestas', () => {
    const { container } = render(<BusinessCopilotPanel message={buildMessage(undefined)} />)
    expect(container).toBeEmptyDOMElement()
  })
})
