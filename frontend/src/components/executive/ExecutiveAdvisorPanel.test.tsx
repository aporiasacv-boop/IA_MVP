import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { ExecutiveAdvisorPanel } from './ExecutiveAdvisorPanel'
import type { ExecutiveAgendaResponse } from '../../services/executiveAdvisorApi'

const sampleAgenda: ExecutiveAgendaResponse = {
  agenda: {
    greeting: 'Buenos días.',
    items: [
      {
        title: 'Concentración comercial',
        summary: 'Los cinco clientes principales concentran actividad.',
        justification: 'Porque representan la mayor parte de la actividad registrada.',
        priority: 'Alta',
        expected_impact: 'Reducir dependencia comercial.',
        suggested_query: 'Muéstrame los principales clientes',
        action_label: 'Analizar',
      },
    ],
  },
  advisor_generation_ms: 12,
  advisor_items: 1,
  advisor_fallback_used: false,
}

describe('ExecutiveAdvisorPanel', () => {
  it('muestra la agenda y ejecuta la consulta al analizar', async () => {
    const onAnalyze = vi.fn()
    const user = userEvent.setup()

    render(<ExecutiveAdvisorPanel data={sampleAgenda} onAnalyze={onAnalyze} />)

    expect(screen.getByText('Agenda Ejecutiva')).toBeInTheDocument()
    expect(screen.getByText('Buenos días.')).toBeInTheDocument()
    expect(screen.getByText('Concentración comercial')).toBeInTheDocument()
    expect(screen.getByText('Porque representan la mayor parte de la actividad registrada.')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Analizar' }))
    expect(onAnalyze).toHaveBeenCalledWith('Muéstrame los principales clientes')
  })
})
