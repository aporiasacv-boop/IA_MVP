/**
 * Feature flags del frontend. Valores desde variables VITE_* en .env
 * para rollback sin cambios de código.
 */
export function isHybridChatEnabled(envValue: string | undefined): boolean {
  return envValue !== 'false'
}

export function isDebugModeEnabled(envValue: string | undefined): boolean {
  return envValue === 'true'
}

export const USE_HYBRID_CHAT = isHybridChatEnabled(import.meta.env.VITE_USE_HYBRID_CHAT)

/** Panel técnico e indicador de origen de respuesta en el chat. */
export const DEBUG_MODE = isDebugModeEnabled(import.meta.env.VITE_DEBUG_MODE)
