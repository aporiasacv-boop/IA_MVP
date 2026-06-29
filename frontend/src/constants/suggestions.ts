export interface SuggestionGroup {
  label: string
  items: string[]
}

/** Sugerencias ejecutivas para Enterprise AI. */
export const SUGGESTION_GROUPS: SuggestionGroup[] = [
  {
    label: 'Decisiones de negocio',
    items: [
      '¿Qué pasó en junio?',
      '¿Quién es nuestro mejor cliente?',
      '¿Cuántos clientes existen?',
      '¿Qué proveedor tuvo más movimiento en junio?',
      'Muéstrame los principales clientes',
    ],
  },
  {
    label: 'Orientación estratégica',
    items: [
      '¿Cómo ves el negocio?',
      '¿Qué debería analizar hoy?',
      '¿Qué puedes hacer?',
      '¿Cuál es el periodo de los datos?',
    ],
  },
]

export const LOADING_MESSAGES = [
  'Interpretando su consulta empresarial…',
  'Consolidando evidencia disponible…',
  'Preparando lectura ejecutiva…',
  'Analizando el contexto del negocio…',
]
