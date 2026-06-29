import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { CapabilityReasoningAuditDebug } from './CapabilityReasoningAuditDebug'
import type { ChatMessage } from '../../types/chat'

const message: ChatMessage = {
  id: 'a-1',
  role: 'assistant',
  content: 'Respuesta de prueba.',
  hybrid: {
    handledBy: 'guided_fallback',
    rawMetadata: {
      audit_selected_capability: 'NONE',
      audit_final_route: 'clarification',
      capability_reasoning_audit: {
        intent: 'customer_analysis',
        decision: {
          selected_capability: 'NONE',
          final_route: 'clarification',
        },
        evaluation: {
          classification: 'Incorrecto',
          summary: 'La consulta cayó en fallback aunque existían capacidades reutilizables.',
          notes: ['TOP_CLIENTES podía responder parcialmente.'],
        },
        report_text: 'Consulta\n---------\nAnaliza el universo de clientes',
      },
    },
  },
}

describe('CapabilityReasoningAuditDebug', () => {
  it('muestra la auditoría solo con metadata disponible', () => {
    render(<CapabilityReasoningAuditDebug message={message} />)

    expect(screen.getByText('Auditoría de razonamiento de capabilities')).toBeInTheDocument()
    expect(screen.getByText('customer_analysis')).toBeInTheDocument()
    expect(screen.getByText('NONE')).toBeInTheDocument()
    expect(screen.getByText('Incorrecto')).toBeInTheDocument()
    expect(
      screen.getByText('La consulta cayó en fallback aunque existían capacidades reutilizables.'),
    ).toBeInTheDocument()
  })
})
