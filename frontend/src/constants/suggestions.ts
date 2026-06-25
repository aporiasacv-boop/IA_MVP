export interface SuggestionGroup {
  label: string
  items: string[]
}

/** Grupos de sugerencias rápidas para el asistente. */
export const SUGGESTION_GROUPS: SuggestionGroup[] = [
  {
    label: 'Consultas empresariales',
    items: [
      '¿Qué pasó en junio?',
      '¿Quién es nuestro mejor cliente?',
      '¿Cuántos clientes existen?',
      '¿Qué proveedor tuvo más movimiento en junio?',
      '¿Cuál es el periodo de los datos?',
    ],
  },
  {
    label: 'Capacidades y alcance',
    items: [
      '¿Qué puedes hacer?',
      '¿Cómo obtienes la información?',
      '¿Qué limitaciones tienes?',
      '¿Qué es un cliente?',
      '¿Qué es una cuenta contable?',
    ],
  },
]

export const LOADING_MESSAGES = [
  'Analizando información...',
  'Consultando indicadores...',
  'Preparando respuesta...',
]
