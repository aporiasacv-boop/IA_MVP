interface AnalyticsCardProps {
  label: string
  value: string
  sub?: string
  tooltip?: string
}

export function AnalyticsCard({ label, value, sub, tooltip }: AnalyticsCardProps) {
  return (
    <div
      className="rounded-2xl border border-olnatura-200 bg-olnatura-50/60 px-4 py-5"
      title={tooltip}
    >
      <p className="text-[11px] text-muted-light">{label}</p>
      <p className="mt-2 text-2xl font-semibold tracking-[-0.02em] text-foreground">{value}</p>
      {sub && <p className="mt-1 text-[11px] text-olnatura-600">{sub}</p>}
      {tooltip && (
        <p className="mt-2 text-[10px] leading-relaxed text-muted" aria-label={tooltip}>
          {tooltip}
        </p>
      )}
    </div>
  )
}
