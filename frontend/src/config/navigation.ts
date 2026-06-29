import { DEBUG_MODE } from './featureFlags'
import { es } from '../i18n/spanish'

export interface NavItem {
  to: string
  label: string
  end?: boolean
  description?: string
}

/** Navegación principal — visible para usuarios ejecutivos. */
export const EXECUTIVE_NAV: NavItem[] = [
  {
    to: '/',
    label: es.nav.enterpriseAi,
    end: true,
    description: es.nav.enterpriseAiDesc,
  },
  {
    to: '/dashboard',
    label: es.nav.executiveDashboard,
    end: false,
    description: es.nav.executiveDashboardDesc,
  },
  {
    to: '/financiero',
    label: es.nav.financialSimulator,
    end: false,
    description: es.nav.financialSimulatorDesc,
  },
]

/** Herramientas técnicas — solo con VITE_DEBUG_MODE=true. */
export const DEBUG_NAV: NavItem[] = [
  { to: '/debug/rendimiento', label: es.nav.performance },
  { to: '/debug/analytics', label: es.nav.analytics },
  { to: '/debug/audit', label: es.nav.audit },
  { to: '/debug/entidades', label: es.nav.entities },
  { to: '/debug/canonicas', label: es.nav.canonical },
  { to: '/debug/perfiles', label: es.nav.profiles },
  { to: '/debug/ontologia', label: es.nav.ontology },
  { to: '/debug/conocimiento', label: es.nav.knowledge },
  { to: '/debug/objetos-conocimiento', label: es.nav.knowledgeObjects },
  { to: '/debug/razonamiento', label: es.nav.reasoning },
  { to: '/debug/intencion-semantica', label: es.nav.semanticIntent },
  { to: '/debug/evidencia', label: es.nav.evidence },
  { to: '/debug/simulador', label: es.nav.simulator },
  { to: '/debug/centro-decisiones', label: es.nav.decisionCenter },
  { to: '/debug/finops', label: es.nav.finops },
]

export function isDebugNavVisible(): boolean {
  return DEBUG_MODE
}
