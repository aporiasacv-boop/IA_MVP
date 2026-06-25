import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  chatSessionManager,
  generateSessionId,
  shouldSuppressFollowUpUi,
} from './chatSessionManager'
import type { HybridChatResult } from '../types/hybrid-chat'

describe('chatSessionManager', () => {
  beforeEach(() => {
    chatSessionManager.resetForTests()
    vi.stubGlobal('crypto', {
      randomUUID: () => 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
    })
  })

  it('generates session id without dashes', () => {
    expect(generateSessionId()).toBe('aaaaaaaabbbbccccddddeeeeeeeeeeee')
  })

  it('creates and reuses session id from sessionStorage', () => {
    const first = chatSessionManager.ensureSessionId()
    expect(first.isNew).toBe(true)
    expect(first.sessionId).toBe('aaaaaaaabbbbccccddddeeeeeeeeeeee')

    const second = chatSessionManager.ensureSessionId()
    expect(second.isNew).toBe(false)
    expect(second.sessionId).toBe(first.sessionId)
  })

  it('updates session id from backend metadata', () => {
    chatSessionManager.setSessionIdFromBackend('backend-session-99')
    expect(chatSessionManager.getSessionId()).toBe('backend-session-99')
  })

  it('tracks pending clarification from slot_clarification response', () => {
    const result: HybridChatResult = {
      handled_by: 'slot_clarification',
      success: true,
      answer: '¿De qué cliente?',
      metadata: {
        session_id: 'sess-1',
        pending_query_type: 'MAX_TRANSACCION_CLIENTE',
      },
    }

    chatSessionManager.syncFromHybridResponse(result)

    expect(chatSessionManager.isPendingClarification()).toBe(true)
    expect(chatSessionManager.getMetrics().clarifications_started).toBe(1)
  })

  it('clears pending and records completion on clarification_resolved', () => {
    chatSessionManager.setPendingClarification(true)
    chatSessionManager.recordClarificationStarted()

    chatSessionManager.syncFromHybridResponse({
      handled_by: 'conversation_memory',
      success: true,
      answer: 'Respuesta',
      metadata: {
        session_id: 'sess-1',
        clarification_resolved: true,
        query_type: 'MAX_TRANSACCION_CLIENTE',
      },
    })

    expect(chatSessionManager.isPendingClarification()).toBe(false)
    expect(chatSessionManager.getMetrics().clarifications_completed).toBe(1)
    expect(chatSessionManager.getClarificationCompletionRate()).toBe(1)
  })

  it('startNewConversation assigns new session id', () => {
    chatSessionManager.ensureSessionId()
    const previous = chatSessionManager.getSessionId()

    vi.stubGlobal('crypto', {
      randomUUID: () => '11111111-2222-3333-4444-555555555555',
    })
    const newId = chatSessionManager.startNewConversation()

    expect(newId).toBe('11111111222233334444555555555555')
    expect(chatSessionManager.getSessionId()).not.toBe(previous)
    expect(chatSessionManager.isPendingClarification()).toBe(false)
    expect(chatSessionManager.getMetrics().conversation_sessions_started).toBe(1)
  })

  it('records session started and reused metrics', () => {
    chatSessionManager.recordSessionStarted()
    chatSessionManager.recordSessionReused()
    chatSessionManager.recordSessionReused()

    const metrics = chatSessionManager.getMetrics()
    expect(metrics.conversation_sessions_started).toBe(1)
    expect(metrics.conversation_sessions_reused).toBe(2)
  })

  it('shouldSuppressFollowUpUi when pending or slot clarification', () => {
    const slot: HybridChatResult = {
      handled_by: 'slot_clarification',
      success: true,
      answer: 'x',
      metadata: {},
    }
    expect(shouldSuppressFollowUpUi(slot, false)).toBe(true)
    expect(
      shouldSuppressFollowUpUi(
        { handled_by: 'business_pipeline', success: true, answer: 'x', metadata: {} },
        true,
      ),
    ).toBe(true)
  })

  it('clears pending when response diverges without clarification flag', () => {
    chatSessionManager.setPendingClarification(true)

    chatSessionManager.syncFromHybridResponse({
      handled_by: 'guided_fallback',
      success: true,
      answer: 'fallback',
      metadata: { session_id: 's1' },
    })

    expect(chatSessionManager.isPendingClarification()).toBe(false)
  })

  it('returns default metrics when stored metrics JSON is invalid', () => {
    sessionStorage.setItem('ia_mvp_chat_session_metrics', '{not-json')
    expect(chatSessionManager.getMetrics()).toEqual({
      conversation_sessions_started: 0,
      conversation_sessions_reused: 0,
      clarifications_started: 0,
      clarifications_completed: 0,
    })
  })

  it('ignores empty session id from backend', () => {
    chatSessionManager.ensureSessionId()
    const before = chatSessionManager.getSessionId()
    chatSessionManager.setSessionIdFromBackend('')
    expect(chatSessionManager.getSessionId()).toBe(before)
  })

  it('shouldSuppressFollowUpUi for capability and fallback routes', () => {
    expect(
      shouldSuppressFollowUpUi(
        { handled_by: 'capability_discovery', success: true, answer: 'x', metadata: {} },
        false,
      ),
    ).toBe(true)
    expect(
      shouldSuppressFollowUpUi(
        { handled_by: 'guided_fallback', success: true, answer: 'x', metadata: {} },
        false,
      ),
    ).toBe(true)
    expect(
      shouldSuppressFollowUpUi(
        { handled_by: 'business_pipeline', success: true, answer: 'x', metadata: {} },
        false,
      ),
    ).toBe(false)
  })
})
