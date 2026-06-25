import { useCallback, useState } from 'react'
import { AdoptionSection } from '../components/operationalAudit/AdoptionSection'
import { AuditOverviewSection } from '../components/operationalAudit/AuditOverviewSection'
import { CoverageGapsTable } from '../components/operationalAudit/CoverageGapsTable'
import { TopFailuresTable } from '../components/operationalAudit/TopFailuresTable'
import { TopRoutesTable } from '../components/operationalAudit/TopRoutesTable'
import { useOperationalAudit } from '../hooks/useOperationalAudit'
import {
  es,
  localizeCoverageGapsCsv,
  localizeCoverageGapsJson,
} from '../i18n/spanish'
import * as operationalAuditApi from '../services/operationalAuditApi'

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

export function OperationalAuditPage() {
  const { data, isLoading, error, refresh } = useOperationalAudit()
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = useCallback(async (format: 'json' | 'csv') => {
    setIsExporting(true)
    try {
      const blob = await operationalAuditApi.exportCoverageGaps(format)
      const raw = await blob.text()
      const localized =
        format === 'csv' ? localizeCoverageGapsCsv(raw) : localizeCoverageGapsJson(raw)
      const localizedBlob = new Blob([localized], {
        type: format === 'csv' ? 'text/csv' : 'application/json',
      })
      downloadBlob(localizedBlob, `${es.audit.exportFilename}.${format}`)
    } finally {
      setIsExporting(false)
    }
  }, [])

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.audit.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em] text-foreground">
            {es.audit.title}
          </h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.audit.subtitle}</p>
        </div>
        <button
          type="button"
          onClick={() => void refresh()}
          disabled={isLoading}
          className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] font-medium text-muted hover:text-foreground disabled:opacity-50"
        >
          {isLoading ? es.common.loading : es.common.refresh}
        </button>
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {es.common.errorAudit}
        </div>
      )}

      <div className="mt-10 space-y-12">
        <AuditOverviewSection overview={data?.overview ?? null} isLoading={isLoading} />
        <CoverageGapsTable
          items={data?.coverageGaps ?? []}
          isLoading={isLoading}
          isExporting={isExporting}
          onExportJson={() => void handleExport('json')}
          onExportCsv={() => void handleExport('csv')}
        />
        <TopFailuresTable items={data?.topFailures ?? []} isLoading={isLoading} />
        <TopRoutesTable items={data?.topRoutes ?? []} isLoading={isLoading} />
        <AdoptionSection adoption={data?.adoption ?? null} isLoading={isLoading} />
      </div>
    </div>
  )
}
