import type { EntityProfileItem } from '../../types/entityProfiles'
import { es } from '../../i18n/spanish'

function formatMoney(value: number): string {
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(value)
}

interface Props {
  items: EntityProfileItem[]
  selectedId?: number
  isLoading: boolean
  onSelect: (canonicalId: number) => void
}

export function ProfileListTable({ items, selectedId, isLoading, onSelect }: Props) {
  return (
    <section>
      <h2 className="text-[13px] font-semibold">{es.entityProfiles.list.title}</h2>
      <p className="mt-1 text-[12px] text-muted">{es.entityProfiles.list.subtitle}</p>
      <div className="mt-4 overflow-x-auto rounded-xl border border-border-subtle">
        <table className="min-w-full text-left text-[12px]">
          <thead className="border-b border-border-subtle bg-surface-elevated text-muted">
            <tr>
              <th className="px-3 py-2 font-medium">{es.entityProfiles.table.name}</th>
              <th className="px-3 py-2 font-medium">{es.entityProfiles.table.movements}</th>
              <th className="px-3 py-2 font-medium">{es.entityProfiles.table.amount}</th>
              <th className="px-3 py-2 font-medium">{es.entityProfiles.table.completeness}</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={4} className="px-3 py-6 text-center text-muted">
                  {es.common.loading}
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-3 py-6 text-center text-muted">
                  {es.common.noData}
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr
                  key={item.profile_id}
                  onClick={() => onSelect(item.canonical_id)}
                  className={`cursor-pointer border-b border-border-subtle/60 hover:bg-surface-elevated/60 ${
                    selectedId === item.canonical_id ? 'bg-surface-elevated' : ''
                  }`}
                >
                  <td className="px-3 py-2 font-medium">{item.canonical_name}</td>
                  <td className="px-3 py-2 tabular-nums">{item.total_movements}</td>
                  <td className="px-3 py-2 tabular-nums">{formatMoney(Number(item.total_amount))}</td>
                  <td className="px-3 py-2 tabular-nums">{(Number(item.profile_completeness) * 100).toFixed(0)}%</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}

interface DetailProps {
  profile: EntityProfileItem | null
  isLoading: boolean
}

export function ProfileDetailPanel({ profile, isLoading }: DetailProps) {
  if (isLoading && !profile) {
    return <p className="text-[12px] text-muted">{es.common.loading}</p>
  }
  if (!profile) {
    return <p className="text-[12px] text-muted">{es.entityProfiles.detail.empty}</p>
  }

  const monthlyEntries = Object.entries(profile.monthly_distribution ?? {}).slice(0, 12)

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-[13px] font-semibold">{es.entityProfiles.detail.title}</h2>
        <p className="mt-1 text-lg font-semibold">{profile.canonical_name}</p>
        {profile.primary_rfc && <p className="text-[12px] text-muted">RFC: {profile.primary_rfc}</p>}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label={es.entityProfiles.detail.activity} value={`${profile.active_months} meses / ${profile.active_days} días`} />
        <MetricCard label={es.entityProfiles.detail.range} value={`${profile.first_seen ?? '—'} → ${profile.last_seen ?? '—'}`} />
        <MetricCard label={es.entityProfiles.detail.debitCredit} value={profile.debit_credit_ratio != null ? String(profile.debit_credit_ratio) : '—'} />
        <MetricCard label={es.entityProfiles.detail.currencies} value={profile.currencies.join(', ') || '—'} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h3 className="text-[12px] font-semibold">{es.entityProfiles.detail.monthly}</h3>
          <ul className="mt-2 space-y-1 text-[12px]">
            {monthlyEntries.map(([period, bucket]) => (
              <li key={period} className="flex justify-between border-b border-border-subtle/40 py-1">
                <span>{period}</span>
                <span className="tabular-nums text-muted">
                  {bucket.movements} mov · {formatMoney(Number(bucket.amount))}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-[12px] font-semibold">{es.entityProfiles.detail.accounts}</h3>
          <ul className="mt-2 space-y-1 text-[12px]">
            {(profile.top_accounts ?? []).slice(0, 5).map((account) => (
              <li key={account.code} className="flex justify-between border-b border-border-subtle/40 py-1">
                <span>{account.code} — {account.name}</span>
                <span className="tabular-nums text-muted">{account.movements}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div>
        <h3 className="text-[12px] font-semibold">{es.entityProfiles.detail.counterparties}</h3>
        <ul className="mt-2 space-y-1 text-[12px]">
          {(profile.top_counterparties ?? []).slice(0, 5).map((cp) => (
            <li key={`${cp.dimension}-${cp.code}`} className="flex justify-between border-b border-border-subtle/40 py-1">
              <span>{cp.code} ({cp.dimension})</span>
              <span className="tabular-nums text-muted">{cp.movements} mov</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2">
      <p className="text-[11px] text-muted">{label}</p>
      <p className="mt-1 text-[13px] font-medium">{value}</p>
    </div>
  )
}
