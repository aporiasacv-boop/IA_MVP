import type { ExperienceScreen } from './types'

export type KpiQuestionKey =
  | 'clients'
  | 'activity'
  | 'operational_health'
  | 'risks'
  | 'alerts'
  | 'efficiency'

export type FinancialMetricKey =
  | 'monthly_cost'
  | 'annual_cost'
  | 'roi'
  | 'llm_savings'
  | 'cost_per_user'
  | 'cost_per_session'
  | 'infrastructure'
  | 'scenario'

const KPI_TEMPLATES: Record<KpiQuestionKey, string> = {
  clients:
    'Analiza el universo de clientes registrados{periodSuffix} y su relevancia para las decisiones comerciales.',
  activity:
    'Analiza la actividad empresarial reciente{periodSuffix} e identifica los movimientos más relevantes.',
  operational_health:
    'Evalúa la salud operativa del negocio{periodSuffix} y señala las áreas que requieren atención ejecutiva.',
  risks:
    'Identifica los principales riesgos de concentración en clientes y proveedores{periodSuffix}.',
  alerts:
    'Resume las señales analíticas más importantes{periodSuffix} y su impacto potencial en el negocio.',
  efficiency:
    'Explica cómo la plataforma resuelve consultas empresariales{periodSuffix} y dónde conviene profundizar.',
}

const FINANCIAL_TEMPLATES: Record<FinancialMetricKey, string> = {
  monthly_cost:
    'Explícame por qué el costo mensual proyectado de la plataforma es el indicado y qué factores lo determinan.',
  annual_cost:
    'Explícame cómo se proyecta el costo anual de operación de Olnatura Intelligence y qué supuestos lo sustentan.',
  roi:
    'Explícame qué retorno de inversión se espera de la plataforma de inteligencia empresarial y cómo se mide.',
  llm_savings:
    'Explícame qué significa el ahorro por eficiencia en el uso de IA y cómo impacta el costo total.',
  cost_per_user:
    'Explícame cómo se calcula el costo por usuario y qué variables lo incrementan o reducen.',
  cost_per_session:
    'Explícame cómo se calcula el costo por sesión conversacional en la plataforma.',
  infrastructure:
    'Explícame qué infraestructura requiere la plataforma y cómo se relaciona con el costo operativo.',
  scenario:
    'Explícame el escenario financiero seleccionado, sus supuestos de adopción y el impacto en costos.',
}

function periodSuffix(period: string | null): string {
  if (!period) return ''
  return ` en el periodo ${period}`
}

export function buildKpiQuestion(key: KpiQuestionKey, period: string | null): string {
  const suffix = periodSuffix(period)
  return KPI_TEMPLATES[key].replace('{periodSuffix}', suffix)
}

export function buildFinancialQuestion(
  key: FinancialMetricKey,
  scenario: string | null,
): string {
  const base = FINANCIAL_TEMPLATES[key]
  if (key === 'scenario' && scenario) {
    return `${base} Escenario: ${scenario}.`
  }
  if (scenario) {
    return `${base} Considera el escenario ${scenario}.`
  }
  return base
}

export function buildContextualSuggestions(context: {
  period: string | null
  scenario: string | null
  lastScreen: ExperienceScreen | null
}): string[] {
  const period = context.period
  const suggestions: string[] = []

  if (context.lastScreen === 'executive_dashboard') {
    suggestions.push(
      period
        ? `¿Qué pasó en ${period}?`
        : '¿Qué debería analizar hoy en el panel ejecutivo?',
    )
    suggestions.push('Muéstrame los principales clientes')
  } else if (context.lastScreen === 'financial_simulator') {
    suggestions.push('Explícame el modelo de costos de la plataforma')
    if (context.scenario) {
      suggestions.push(`¿Qué implica el escenario ${context.scenario}?`)
    }
  } else {
    suggestions.push('¿Cómo ves el negocio?')
    suggestions.push('¿Qué puedes hacer?')
  }

  if (period) {
    suggestions.push(`Resume la actividad de ${period}`)
  }

  return [...new Set(suggestions)].slice(0, 5)
}
