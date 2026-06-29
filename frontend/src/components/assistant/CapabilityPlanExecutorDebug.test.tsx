import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { CapabilityPlanExecutorDebug } from './CapabilityPlanExecutorDebug'
import type { ChatMessage } from '../../types/chat'

const message: ChatMessage = {
  id: 'a-3',
  role: 'assistant',
  content: 'Respuesta.',
  hybrid: {
    handledBy: 'business_pipeline',
    rawMetadata: {
      plan_executed: true,
      execution_strategy: 'SINGLE',
      primary_capability: 'TOP_CLIENTES',
      coverage_used: 85,
      fallback_avoided: true,
      execution_time_ms: 12.4,
      partial_execution: false,
    },
  },
}

describe('CapabilityPlanExecutorDebug', () => {
  it('muestra la ejecución del plan en modo debug', () => {
    render(<CapabilityPlanExecutorDebug message={message} />)

    expect(screen.getByText('Capability Plan Executor')).toBeInTheDocument()
    expect(screen.getByText('SINGLE')).toBeInTheDocument()
    expect(screen.getByText('TOP_CLIENTES')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('Sí')).toBeInTheDocument()
    expect(screen.getByText('12.4 ms')).toBeInTheDocument()
  })
})
