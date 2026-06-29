import { beforeEach, describe, expect, it, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useChatApi } from './useChatApi'
import { chatSessionManager } from '../services/chatSessionManager'
import { enterpriseExperienceStore } from '../enterpriseExperience/store'
import * as chatApi from '../services/chatApi'

vi.mock('../services/performanceStore', () => ({
  recordChatResponse: vi.fn(),
  recordHybridResponse: vi.fn(),
}))

describe('useChatApi multi-turn', () => {
  beforeEach(() => {
    chatSessionManager.resetForTests()
    enterpriseExperienceStore._resetForTests()
    vi.restoreAllMocks()
    vi.stubGlobal('crypto', {
      randomUUID: () => 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
    })
  })

  it('marca aclaración pendiente tras slot_clarification', async () => {
    const response = {
      handled_by: 'slot_clarification',
      success: true,
      answer: '¿De qué cliente?',
      metadata: { session_id: 's1', pending_query_type: 'MAX_TRANSACCION_CLIENTE' },
    }
    vi.spyOn(chatApi, 'sendChatQuestion').mockImplementation(async () => {
      chatSessionManager.syncFromHybridResponse(response)
      return response
    })

    const { result } = renderHook(() => useChatApi())

    await act(async () => {
      await result.current.submitQuestion('¿Cuál fue la transacción más alta?')
    })

    await waitFor(() => {
      expect(result.current.isClarificationPending).toBe(true)
    })
  })

  it('libera aclaración tras conversation_memory resuelta', async () => {
    const first = {
      handled_by: 'slot_clarification',
      success: true,
      answer: '¿De qué cliente?',
      metadata: { session_id: 's1' },
    }
    const second = {
      handled_by: 'conversation_memory',
      success: true,
      answer: 'Máxima transacción',
      metadata: {
        session_id: 's1',
        clarification_resolved: true,
        query_type: 'MAX_TRANSACCION_CLIENTE',
      },
    }
    vi.spyOn(chatApi, 'sendChatQuestion')
      .mockImplementationOnce(async () => {
        chatSessionManager.syncFromHybridResponse(first)
        return first
      })
      .mockImplementationOnce(async () => {
        chatSessionManager.syncFromHybridResponse(second)
        return second
      })

    const { result } = renderHook(() => useChatApi())

    await act(async () => {
      await result.current.submitQuestion('¿Cuál fue la transacción más alta?')
    })
    await act(async () => {
      await result.current.submitQuestion('C0003')
    })

    await waitFor(() => {
      expect(result.current.isClarificationPending).toBe(false)
      expect(result.current.messages).toHaveLength(4)
    })
  })

  it('startNewConversation genera nuevo session_id', () => {
    chatSessionManager.ensureSessionId()
    const before = chatSessionManager.getSessionId()

    vi.stubGlobal('crypto', {
      randomUUID: () => '11111111-2222-3333-4444-555555555555',
    })

    const { result } = renderHook(() => useChatApi())

    act(() => {
      result.current.startNewConversation()
    })

    expect(chatSessionManager.getSessionId()).not.toBe(before)
    expect(result.current.messages).toHaveLength(0)
  })
})
