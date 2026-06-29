import { USE_HYBRID_CHAT } from '../config/featureFlags'

import type { ChatApiResponse, ChatMessage, ResponseMode } from '../types/chat'

import { ChatApiError } from '../types/chat'

import type { HybridChatResult } from '../types/hybrid-chat'

import { chatSessionManager } from './chatSessionManager'



export type ChatQuestionResult = ChatApiResponse | HybridChatResult



function getApiBaseUrl(): string {

  const base = import.meta.env.VITE_API_BASE_URL ?? ''

  return base.replace(/\/$/, '')

}



export function isHybridChatResult(result: ChatQuestionResult): result is HybridChatResult {

  return 'handled_by' in result

}



async function postJson<T>(path: string, body: unknown): Promise<T> {

  const baseUrl = getApiBaseUrl()

  const url = `${baseUrl}${path}`



  let response: Response

  try {

    response = await fetch(url, {

      method: 'POST',

      headers: {

        'Content-Type': 'application/json',

        Accept: 'application/json',

      },

      body: JSON.stringify(body),

    })

  } catch {

    throw new ChatApiError('No fue posible obtener una respuesta del sistema.')

  }



  if (!response.ok) {

    throw new ChatApiError('No fue posible obtener una respuesta del sistema.')

  }



  try {

    return (await response.json()) as T

  } catch {

    throw new ChatApiError('No fue posible obtener una respuesta del sistema.')

  }

}



export async function sendLegacyChatQuestion(question: string): Promise<ChatApiResponse> {

  return postJson<ChatApiResponse>('/api/chat', { question })

}



export async function sendHybridChatQuestion(message: string): Promise<HybridChatResult> {

  const { sessionId, isNew } = chatSessionManager.ensureSessionId()

  if (isNew) {

    chatSessionManager.recordSessionStarted()

  } else {

    chatSessionManager.recordSessionReused()

  }



  const result = await postJson<HybridChatResult>('/api/chat/hybrid', {

    message,

    session_id: sessionId,

  })



  chatSessionManager.syncFromHybridResponse(result)

  return result

}



export async function sendChatQuestion(question: string): Promise<ChatQuestionResult> {

  if (USE_HYBRID_CHAT) {

    return sendHybridChatQuestion(question)

  }

  return sendLegacyChatQuestion(question)

}



export function mapApiResponseToMessage(response: ChatApiResponse, id: string): ChatMessage {

  return {

    id,

    role: 'assistant',

    content: response.answer,

    intent: response.intent,

    intentConfidence: response.intent_confidence,

    responseMode: response.response_mode,

    timings: response.timings,

    promptMetrics: response.prompt_metrics,

    sources: response.sources,

    timestamp: new Date(),

  }

}



function readMetadataString(metadata: Record<string, unknown>, key: string): string | undefined {

  const value = metadata[key]

  return typeof value === 'string' ? value : undefined

}



function readMetadataNumber(metadata: Record<string, unknown>, key: string): number | undefined {

  const value = metadata[key]

  return typeof value === 'number' ? value : undefined

}



function readMetadataBoolean(metadata: Record<string, unknown>, key: string): boolean | undefined {

  const value = metadata[key]

  return typeof value === 'boolean' ? value : undefined

}



export function mapHybridChatResultToMessage(response: HybridChatResult, id: string): ChatMessage {

  const queryType = readMetadataString(response.metadata, 'query_type')

  const confidence = readMetadataNumber(response.metadata, 'confidence')

  const legacyIntent = readMetadataString(response.metadata, 'intent')

  const legacyMode = readMetadataString(response.metadata, 'response_mode') as ResponseMode | undefined

  const clarificationResolved = readMetadataBoolean(response.metadata, 'clarification_resolved')

  const pendingQueryType = readMetadataString(response.metadata, 'pending_query_type')



  const responseMode: ResponseMode | undefined =

    response.handled_by === 'business_pipeline'

      ? 'DETERMINISTIC'

      : legacyMode



  const conversationUxApplied = response.metadata?.conversation_ux_applied === true

  const suppressFollowUp =
    !conversationUxApplied &&
    (chatSessionManager.isPendingClarification() ||
      response.handled_by === 'slot_clarification' ||
      response.handled_by === 'capability_discovery' ||
      response.handled_by === 'guided_fallback')



  const suggestedQuestions = suppressFollowUp

    ? []

    : (response.suggestions?.questions ?? [])



  return {

    id,

    role: 'assistant',

    content: response.answer,

    intent: queryType ?? legacyIntent,

    intentConfidence: confidence,

    responseMode,

    suggestedQuestions,

    hybrid: {

      handledBy: response.handled_by,

      queryType,

      confidence,

      success: response.success,

      rawMetadata: response.metadata,

      sessionId: readMetadataString(response.metadata, 'session_id'),

      pendingClarification: response.handled_by === 'slot_clarification' || !!pendingQueryType,

      clarificationResolved,

    },

    timestamp: new Date(),

  }

}


