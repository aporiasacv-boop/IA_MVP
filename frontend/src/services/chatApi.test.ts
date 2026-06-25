import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  isHybridChatResult,
  mapApiResponseToMessage,
  mapHybridChatResultToMessage,
  sendChatQuestion,
  sendHybridChatQuestion,
  sendLegacyChatQuestion,
} from './chatApi'
import { chatSessionManager } from './chatSessionManager'
import type { ChatApiResponse } from '../types/chat'
import { ChatApiError } from '../types/chat'
import type { HybridChatResult } from '../types/hybrid-chat'

vi.mock('../config/featureFlags', () => ({
  USE_HYBRID_CHAT: true,
}))

describe('chatApi hybrid', () => {
  beforeEach(() => {
    chatSessionManager.resetForTests()
    vi.restoreAllMocks()
  })

  const pipelineResult: HybridChatResult = {
    handled_by: 'business_pipeline',
    success: true,
    answer: 'Actualmente existen 50 clientes registrados.',
    metadata: {
      query_type: 'COUNT_CLIENTES',
      confidence: 1.0,
      session_id: 'server-session-1',
    },
    suggestions: { questions: ['¿Cuántos proveedores?'], source: 'rules', confidence: 1, metadata: {} },
  }

  const legacyResult: HybridChatResult = {
    handled_by: 'legacy_chat',
    success: true,
    answer: 'Hola, soy el asistente.',
    metadata: {
      intent: 'GREETING',
      confidence: 0.95,
      response_mode: 'GENERATIVE',
    },
  }

  const clarificationResult: HybridChatResult = {
    handled_by: 'slot_clarification',
    success: true,
    answer: '¿De qué cliente deseas consultar la información?',
    metadata: {
      pending_query_type: 'MAX_TRANSACCION_CLIENTE',
      session_id: 'backend-sess-abc',
    },
  }

  it('identifica HybridChatResult por handled_by', () => {
    expect(isHybridChatResult(pipelineResult)).toBe(true)
    expect(
      isHybridChatResult({
        intent: 'X',
        answer: 'y',
        intent_confidence: 1,
        response_mode: 'DETERMINISTIC',
      } as never),
    ).toBe(false)
  })

  it('mapea respuesta del business pipeline a ChatMessage', () => {
    const message = mapHybridChatResultToMessage(pipelineResult, 'a-1')

    expect(message.content).toBe(pipelineResult.answer)
    expect(message.hybrid?.handledBy).toBe('business_pipeline')
    expect(message.hybrid?.queryType).toBe('COUNT_CLIENTES')
    expect(message.hybrid?.confidence).toBe(1.0)
    expect(message.responseMode).toBe('DETERMINISTIC')
    expect(message.suggestedQuestions).toHaveLength(1)
  })

  it('mapea respuesta legacy enrutada por hybrid a ChatMessage', () => {
    const message = mapHybridChatResultToMessage(legacyResult, 'a-2')

    expect(message.content).toBe(legacyResult.answer)
    expect(message.hybrid?.handledBy).toBe('legacy_chat')
    expect(message.intent).toBe('GREETING')
    expect(message.responseMode).toBe('GENERATIVE')
  })

  it('oculta sugerencias en slot_clarification', () => {
    const message = mapHybridChatResultToMessage(
      {
        ...clarificationResult,
        suggestions: { questions: ['x'], source: 'rules', confidence: 1, metadata: {} },
      },
      'a-3',
    )

    expect(message.suggestedQuestions).toEqual([])
    expect(message.hybrid?.pendingClarification).toBe(true)
  })

  it('sendHybridChatQuestion envía message y session_id', async () => {
    vi.stubGlobal('crypto', {
      randomUUID: () => 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
    })

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => clarificationResult,
    })
    vi.stubGlobal('fetch', fetchMock)

    await sendHybridChatQuestion('¿Cuál fue la transacción más alta?')

    expect(fetchMock).toHaveBeenCalledOnce()
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    const body = JSON.parse(init.body as string) as { message: string; session_id: string }
    expect(body.message).toBe('¿Cuál fue la transacción más alta?')
    expect(body.session_id).toBe('aaaaaaaabbbbccccddddeeeeeeeeeeee')
    expect(chatSessionManager.getSessionId()).toBe('backend-sess-abc')
    expect(chatSessionManager.isPendingClarification()).toBe(true)
  })

  it('reutiliza session_id en segundo turno C0003', async () => {
    vi.stubGlobal('crypto', {
      randomUUID: () => 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
    })

    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => clarificationResult,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () =>
          ({
            handled_by: 'conversation_memory',
            success: true,
            answer: 'Transacción máxima',
            metadata: {
              session_id: 'backend-sess-abc',
              clarification_resolved: true,
              query_type: 'MAX_TRANSACCION_CLIENTE',
            },
          }) satisfies HybridChatResult,
      })
    vi.stubGlobal('fetch', fetchMock)

    await sendHybridChatQuestion('¿Cuál fue la transacción más alta?')
    await sendHybridChatQuestion('C0003')

    const secondBody = JSON.parse(
      (fetchMock.mock.calls[1] as [string, RequestInit])[1].body as string,
    ) as { session_id: string }

    expect(secondBody.session_id).toBe('backend-sess-abc')
    expect(chatSessionManager.isPendingClarification()).toBe(false)
    expect(chatSessionManager.getMetrics().conversation_sessions_reused).toBe(1)
  })

  it('reutiliza session_id en clarificación proveedor + mes', async () => {
    vi.stubGlobal('crypto', {
      randomUUID: () => 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
    })

    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () =>
          ({
            handled_by: 'slot_clarification',
            success: true,
            answer: '¿De qué mes?',
            metadata: {
              session_id: 'prov-session',
              pending_query_type: 'MAX_PROVEEDOR_MES',
            },
          }) satisfies HybridChatResult,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () =>
          ({
            handled_by: 'conversation_memory',
            success: true,
            answer: 'Proveedor con mayor movimiento',
            metadata: {
              session_id: 'prov-session',
              clarification_resolved: true,
              query_type: 'MAX_PROVEEDOR_MES',
            },
          }) satisfies HybridChatResult,
      })
    vi.stubGlobal('fetch', fetchMock)

    await sendHybridChatQuestion('¿Qué proveedor tuvo más movimiento?')
    await sendHybridChatQuestion('junio')

    const secondBody = JSON.parse(
      (fetchMock.mock.calls[1] as [string, RequestInit])[1].body as string,
    ) as { session_id: string }
    expect(secondBody.session_id).toBe('prov-session')
    expect(chatSessionManager.getClarificationCompletionRate()).toBe(1)
  })

  it('sendLegacyChatQuestion envía question al endpoint legacy', async () => {
    const legacyResponse: ChatApiResponse = {
      intent: 'COUNT_CLIENTES',
      intent_confidence: 1,
      response_mode: 'DETERMINISTIC',
      answer: '50 clientes',
      data: null,
      original_question: '¿Cuántos clientes?',
      normalized_question: 'cuantos clientes',
      corrections_applied: [],
      entities: {},
      sources: [],
      timings: {
        spell_correction_ms: 0,
        synonym_resolution_ms: 0,
        intent_normalization_ms: 0,
        entity_extraction_ms: 0,
        router_ms: 0,
        deterministic_ms: 0,
        query_ms: 0,
        context_ms: 0,
        prompt_ms: 0,
        llm_ms: 0,
        total_ms: 1,
      },
      prompt_metrics: {
        prompt_chars: 0,
        context_chars: 0,
        question_chars: 0,
        response_chars: 0,
        estimated_tokens: 0,
        sources_used: [],
      },
    }

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => legacyResponse,
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await sendLegacyChatQuestion('¿Cuántos clientes?')

    expect(result.answer).toBe('50 clientes')
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain('/api/chat')
    expect(JSON.parse(init.body as string)).toEqual({ question: '¿Cuántos clientes?' })
  })

  it('sendChatQuestion delega a hybrid cuando USE_HYBRID_CHAT está activo', async () => {
    vi.stubGlobal('crypto', {
      randomUUID: () => 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
    })
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => pipelineResult,
      }),
    )

    const result = await sendChatQuestion('hola')
    expect(isHybridChatResult(result)).toBe(true)
  })

  it('mapApiResponseToMessage mapea respuesta legacy a ChatMessage', () => {
    const response: ChatApiResponse = {
      intent: 'GREETING',
      intent_confidence: 0.9,
      response_mode: 'GENERATIVE',
      answer: 'Hola',
      data: null,
      original_question: 'hola',
      normalized_question: 'hola',
      corrections_applied: [],
      entities: {},
      sources: ['kb'],
      timings: {
        spell_correction_ms: 0,
        synonym_resolution_ms: 0,
        intent_normalization_ms: 0,
        entity_extraction_ms: 0,
        router_ms: 0,
        deterministic_ms: 0,
        query_ms: 0,
        context_ms: 0,
        prompt_ms: 0,
        llm_ms: 0,
        total_ms: 1,
      },
      prompt_metrics: {
        prompt_chars: 1,
        context_chars: 2,
        question_chars: 3,
        response_chars: 4,
        estimated_tokens: 5,
        sources_used: ['kb'],
      },
    }

    const message = mapApiResponseToMessage(response, 'msg-1')
    expect(message.id).toBe('msg-1')
    expect(message.role).toBe('assistant')
    expect(message.content).toBe('Hola')
    expect(message.intent).toBe('GREETING')
    expect(message.sources).toEqual(['kb'])
  })

  it('oculta sugerencias en capability_discovery y guided_fallback', () => {
    const capability: HybridChatResult = {
      handled_by: 'capability_discovery',
      success: true,
      answer: 'Puedo ayudarte con...',
      metadata: {},
      suggestions: { questions: ['q1'], source: 'rules', confidence: 1, metadata: {} },
    }
    const fallback: HybridChatResult = {
      handled_by: 'guided_fallback',
      success: true,
      answer: 'No entendí',
      metadata: {},
      suggestions: { questions: ['q2'], source: 'rules', confidence: 1, metadata: {} },
    }

    expect(mapHybridChatResultToMessage(capability, 'c-1').suggestedQuestions).toEqual([])
    expect(mapHybridChatResultToMessage(fallback, 'c-2').suggestedQuestions).toEqual([])
  })

  it('oculta sugerencias cuando el manager tiene aclaración pendiente', () => {
    chatSessionManager.setPendingClarification(true)

    const message = mapHybridChatResultToMessage(pipelineResult, 'a-pending')
    expect(message.suggestedQuestions).toEqual([])
  })

  it('mapea clarification_resolved y sessionId en hybrid metadata', () => {
    const resolved: HybridChatResult = {
      handled_by: 'conversation_memory',
      success: true,
      answer: 'Listo',
      metadata: {
        session_id: 'sess-resolved',
        clarification_resolved: true,
        query_type: 'MAX_TRANSACCION_CLIENTE',
        confidence: 0.99,
      },
    }

    const message = mapHybridChatResultToMessage(resolved, 'r-1')
    expect(message.hybrid?.sessionId).toBe('sess-resolved')
    expect(message.hybrid?.clarificationResolved).toBe(true)
    expect(message.intent).toBe('MAX_TRANSACCION_CLIENTE')
    expect(message.intentConfidence).toBe(0.99)
  })

  it('lanza ChatApiError cuando fetch falla', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network')))
    await expect(sendHybridChatQuestion('hola')).rejects.toBeInstanceOf(ChatApiError)
  })

  it('lanza ChatApiError cuando la respuesta HTTP no es ok', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
      }),
    )
    await expect(sendHybridChatQuestion('hola')).rejects.toBeInstanceOf(ChatApiError)
  })

  it('lanza ChatApiError cuando el cuerpo no es JSON válido', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => {
          throw new Error('invalid json')
        },
      }),
    )
    await expect(sendHybridChatQuestion('hola')).rejects.toBeInstanceOf(ChatApiError)
  })
})

describe('sendChatQuestion legacy routing', () => {
  beforeEach(() => {
    chatSessionManager.resetForTests()
    vi.restoreAllMocks()
  })

  it('delega a legacy cuando USE_HYBRID_CHAT está desactivado', async () => {
    vi.resetModules()
    vi.doMock('../config/featureFlags', () => ({
      USE_HYBRID_CHAT: false,
    }))

    const { sendChatQuestion } = await import('./chatApi')
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        intent: 'GREETING',
        intent_confidence: 1,
        response_mode: 'GENERATIVE',
        answer: 'Hola',
        data: null,
        original_question: 'hola',
        normalized_question: 'hola',
        corrections_applied: [],
        entities: {},
        sources: [],
        timings: {
          spell_correction_ms: 0,
          synonym_resolution_ms: 0,
          intent_normalization_ms: 0,
          entity_extraction_ms: 0,
          router_ms: 0,
          deterministic_ms: 0,
          query_ms: 0,
          context_ms: 0,
          prompt_ms: 0,
          llm_ms: 0,
          total_ms: 1,
        },
        prompt_metrics: {
          prompt_chars: 0,
          context_chars: 0,
          question_chars: 0,
          response_chars: 0,
          estimated_tokens: 0,
          sources_used: [],
        },
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await sendChatQuestion('hola')
    expect(isHybridChatResult(result)).toBe(false)
    expect((result as ChatApiResponse).answer).toBe('Hola')
  })
})
