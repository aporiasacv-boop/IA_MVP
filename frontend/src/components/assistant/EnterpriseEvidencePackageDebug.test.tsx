import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { EnterpriseEvidencePackageDebug } from './EnterpriseEvidencePackageDebug'
import type { ChatMessage } from '../../types/chat'

const message: ChatMessage = {
  id: '1',
  role: 'assistant',
  content: 'Respuesta.',
  hybrid: {
    handledBy: 'business_pipeline',
    rawMetadata: {
      enterprise_evidence_package: {
        business_goal: 'Analizar salud comercial',
        coverage: 92,
        evidence_items: [
          { evidence_label: 'Principales clientes', capability: 'TOP_CLIENTES' },
          { evidence_label: 'Indicadores clave', capability: 'KPIS' },
        ],
        missing_evidence: [],
      },
      executed_capabilities: ['DATA_COVERAGE', 'TOP_CLIENTES', 'KPIS'],
      package_coverage: 92,
    },
  },
}

describe('EnterpriseEvidencePackageDebug', () => {
  it('muestra el paquete de evidencia cuando existe metadata', () => {
    render(<EnterpriseEvidencePackageDebug message={message} />)
    expect(screen.getByText(/Paquete de evidencia empresarial/i)).toBeInTheDocument()
    expect(screen.getByText(/Analizar salud comercial/i)).toBeInTheDocument()
    expect(screen.getByText(/TOP_CLIENTES/i)).toBeInTheDocument()
  })

  it('no renderiza sin enterprise_evidence_package', () => {
    const empty: ChatMessage = { ...message, hybrid: { handledBy: 'guided_fallback' } }
    const { container } = render(<EnterpriseEvidencePackageDebug message={empty} />)
    expect(container).toBeEmptyDOMElement()
  })
})
