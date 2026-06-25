export interface SuggestionGroup {
  label: string
  items: string[]
}

export const SUGGESTION_GROUPS: SuggestionGroup[] = [
  {
    label: 'Consultas empresariales',
    items: [
      '¿Qué pasó en junio?',
      '¿Quién es nuestro mejor cliente?',
      'Resume 2025',
      '¿Qué insights detectaste?',
      '¿Cómo optimizas costos?',
    ],
  },
  {
    label: 'Capacidades y alcance',
    items: [
      '¿Qué puedes hacer?',
      '¿Qué no puedes hacer?',
      '¿Puedes hacer gráficas?',
      '¿Puedes comparar meses?',
      '¿Puedes hacer predicciones?',
      '¿Qué limitaciones tienes?',
    ],
  },
]

/** @deprecated Usar SUGGESTION_GROUPS */
export const QUICK_SUGGESTIONS = SUGGESTION_GROUPS.flatMap((group) => group.items)

export const LOADING_MESSAGES = [
  'Analizando información...',
  'Consultando indicadores...',
  'Preparando respuesta...',
]
