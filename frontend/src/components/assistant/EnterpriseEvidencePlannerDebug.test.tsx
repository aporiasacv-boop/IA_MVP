import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { EnterpriseEvidencePlannerDebug } from './EnterpriseEvidencePlannerDebug'
import type { ChatMessage } from '../../types/chat'

const message: ChatMessage = {
  id: 'a-4',
  role: 'assistant',
  content: 'Respuesta.',
  hybrid: {
    handledBy: 'guided_fallback',
    rawMetadata: {
      business_goal: 'Analizar salud comercial',
      estimated_coverage: 94,
      required_evidence: ['Principales clientes', 'Indicadores clave del negocio', 'Cobertura temporal de datos'],
      required_capabilities: ['TOP_CLIENTES', 'KPIS', 'DATA_COVERAGE'],
      enterprise_evidence_plan: {
        business_goal: 'Analizar salud comercial',
        estimated_coverage: 94,
        required_evidence: ['Principales clientes', 'Indicadores clave del negocio', 'Cobertura temporal de datos'],
        required_capabilities: ['TOP_CLIENTES', 'KPIS', 'DATA_COVERAGE'],
      },
    },
  },
}

describe('EnterpriseEvidencePlannerDebug', () => {
  it('muestra el plan de evidencia en modo debug', () => {
    render(<EnterpriseEvidencePlannerDebug message={message} />)

    expect(screen.getByText('Enterprise Evidence Planner')).toBeInTheDocument()
    expect(screen.getByText('Analizar salud comercial')).toBeInTheDocument()
    expect(screen.getByText('94%')).toBeInTheDocument()
    expect(screen.getByText('Principales clientes')).toBeInTheDocument()
    expect(screen.getByText('TOP_CLIENTES · KPIS · DATA_COVERAGE')).toBeInTheDocument()
  })
})
