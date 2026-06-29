import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
  type ReactNode,
} from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { buildContextualSuggestions } from './questions'
import { enterpriseExperienceStore, pathToScreen } from './store'
import type { ExperienceScreen, NavigationTelemetry } from './types'

interface NavigateToAiOptions {
  origin: string
  intent?: 'analyze' | 'explain'
  deepLink?: boolean
  contextPatch?: {
    period?: string | null
    scenario?: string | null
    company?: string | null
  }
}

interface EnterpriseExperienceValue {
  context: ReturnType<typeof enterpriseExperienceStore.getContext>
  pinnedQueries: ReturnType<typeof enterpriseExperienceStore.getSnapshot>['pinnedQueries']
  recentQueries: ReturnType<typeof enterpriseExperienceStore.getSnapshot>['recentQueries']
  conversation: ReturnType<typeof enterpriseExperienceStore.getSnapshot>['conversation']
  lastNavigation: NavigationTelemetry | null
  contextualSuggestions: string[]
  navigateToAi: (question: string, options: NavigateToAiOptions) => void
  navigateToScreen: (target: ExperienceScreen, params?: Record<string, string>) => void
  syncFromSearchParams: (params: URLSearchParams) => boolean
  togglePin: (question: string) => void
  isPinned: (question: string) => boolean
  recordScreenView: (screen: ExperienceScreen) => void
}

const EnterpriseExperienceContext = createContext<EnterpriseExperienceValue | null>(null)

export function EnterpriseExperienceProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const location = useLocation()
  const storeSnapshot = useSyncExternalStore(
    enterpriseExperienceStore.subscribe,
    enterpriseExperienceStore.getSnapshot,
    enterpriseExperienceStore.getSnapshot,
  )

  const navigateToAi = useCallback(
    (question: string, options: NavigateToAiOptions) => {
      const trimmed = question.trim()
      if (!trimmed) return

      const origin = pathToScreen(location.pathname)
      if (options.contextPatch) {
        enterpriseExperienceStore.setContext(options.contextPatch)
      }
      enterpriseExperienceStore.setContext({
        lastQuery: trimmed,
        lastScreen: 'enterprise_ai',
      })
      enterpriseExperienceStore.recordNavigation({
        navigation_origin: options.origin || origin,
        navigation_target: 'enterprise_ai',
        deep_link_used: options.deepLink ?? false,
        context_restored: storeSnapshot.conversation.length > 0,
      })

      const params = new URLSearchParams()
      params.set('q', trimmed)
      if (options.intent) params.set('intent', options.intent)
      navigate(`/?${params.toString()}`)
    },
    [location.pathname, navigate, storeSnapshot.conversation.length],
  )

  const navigateToScreen = useCallback(
    (target: ExperienceScreen, params: Record<string, string> = {}) => {
      const origin = pathToScreen(location.pathname)
      const paths: Record<ExperienceScreen, string> = {
        enterprise_ai: '/',
        executive_dashboard: '/dashboard',
        financial_simulator: '/financiero',
      }
      const search = new URLSearchParams(params).toString()
      const path = search ? `${paths[target]}?${search}` : paths[target]

      enterpriseExperienceStore.setContext({ lastScreen: target })
      enterpriseExperienceStore.recordNavigation({
        navigation_origin: origin,
        navigation_target: target,
        deep_link_used: Object.keys(params).length > 0,
        context_restored: true,
      })
      navigate(path)
    },
    [location.pathname, navigate],
  )

  const syncFromSearchParams = useCallback((params: URLSearchParams): boolean => {
    let restored = false
    const period = params.get('period')
    const scenario = params.get('scenario')
    const company = params.get('company')

    if (period) {
      enterpriseExperienceStore.setContext({ period })
      restored = true
    }
    if (scenario) {
      enterpriseExperienceStore.setContext({ scenario })
      restored = true
    }
    if (company) {
      enterpriseExperienceStore.setContext({ company })
      restored = true
    }
    return restored
  }, [])

  const recordScreenView = useCallback(
    (screen: ExperienceScreen) => {
      enterpriseExperienceStore.setContext({ lastScreen: screen })
    },
    [],
  )

  const value = useMemo<EnterpriseExperienceValue>(
    () => ({
      context: storeSnapshot.context,
      pinnedQueries: storeSnapshot.pinnedQueries,
      recentQueries: storeSnapshot.recentQueries,
      conversation: storeSnapshot.conversation,
      lastNavigation: storeSnapshot.lastNavigation,
      contextualSuggestions: buildContextualSuggestions({
        period: storeSnapshot.context.period,
        scenario: storeSnapshot.context.scenario,
        lastScreen: storeSnapshot.context.lastScreen,
      }),
      navigateToAi,
      navigateToScreen,
      syncFromSearchParams,
      togglePin: enterpriseExperienceStore.togglePin,
      isPinned: enterpriseExperienceStore.isPinned,
      recordScreenView,
    }),
    [navigateToAi, navigateToScreen, recordScreenView, storeSnapshot, syncFromSearchParams],
  )

  return (
    <EnterpriseExperienceContext.Provider value={value}>
      {children}
    </EnterpriseExperienceContext.Provider>
  )
}

export function useEnterpriseExperience(): EnterpriseExperienceValue {
  const ctx = useContext(EnterpriseExperienceContext)
  if (!ctx) {
    throw new Error('useEnterpriseExperience debe usarse dentro de EnterpriseExperienceProvider')
  }
  return ctx
}
