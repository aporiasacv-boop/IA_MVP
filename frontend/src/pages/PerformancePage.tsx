import { ArchitecturalExplanation } from '../components/performance/ArchitecturalExplanation'
import { BackendMetricsSection } from '../components/performance/BackendMetricsSection'
import { ExecutiveSummarySection } from '../components/performance/ExecutiveSummarySection'
import { SmartSavingsHero } from '../components/performance/SmartSavingsHero'
import { useBackendMetrics } from '../hooks/useBackendMetrics'
import { usePerformanceMetrics } from '../hooks/usePerformanceMetrics'

export function PerformancePage() {
  const {
    data: backendData,
    isLoading: backendLoading,
    error: backendError,
    refresh: refreshBackend,
  } = useBackendMetrics()
  const { metrics, savingsExample, isLoading, error, refresh } = usePerformanceMetrics()

  return (
    <div className="h-full overflow-y-auto pb-12">
      {error && (
        <div className="mx-4 mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 md:mx-8">
          {error}
        </div>
      )}

      <BackendMetricsSection
        data={backendData}
        isLoading={backendLoading}
        error={backendError}
        onRefresh={refreshBackend}
      />

      <div className="border-t border-border-subtle" />

      <ExecutiveSummarySection metrics={metrics} isLoading={isLoading} onRefresh={refresh} />
      <SmartSavingsHero example={savingsExample} isLoading={isLoading} />
      <ArchitecturalExplanation />
    </div>
  )
}
