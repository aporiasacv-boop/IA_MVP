import { useEffect, type ReactNode } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { DEBUG_MODE } from '../../config/featureFlags'
import { DEBUG_NAV, EXECUTIVE_NAV, isDebugNavVisible } from '../../config/navigation'
import { useEnterpriseExperience } from '../../enterpriseExperience'
import type { ExperienceScreen } from '../../enterpriseExperience'
import { es } from '../../i18n/spanish'

interface EnterpriseUnifiedHeaderProps {
  title: string
  subtitle?: string
}

export function EnterpriseUnifiedHeader({ title, subtitle }: EnterpriseUnifiedHeaderProps) {
  const { context, lastNavigation } = useEnterpriseExperience()
  const location = useLocation()

  return (
    <header className="shrink-0 border-b border-border-subtle/80 bg-surface-elevated/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-4 md:px-8">
        <div className="min-w-0 flex-1">
          <EnterpriseBreadcrumb pathname={location.pathname} />
          <h1 className="mt-2 text-[1.05rem] font-semibold tracking-[-0.02em] text-foreground md:text-lg">
            {title}
          </h1>
          {subtitle && (
            <p className="mt-1 max-w-2xl text-[13px] leading-5 text-muted">{subtitle}</p>
          )}
        </div>
        <ContextChips context={context} />
      </div>
      {DEBUG_MODE && lastNavigation && (
        <div className="border-t border-border-subtle/60 bg-surface-subtle/50 px-4 py-2 text-[10px] text-muted md:px-8">
          {es.experience.telemetry}: {lastNavigation.navigation_origin} →{' '}
          {lastNavigation.navigation_target}
          {lastNavigation.deep_link_used ? ' · deep_link' : ''}
          {lastNavigation.context_restored ? ' · context_restored' : ''}
        </div>
      )}
    </header>
  )
}

function EnterpriseBreadcrumb({ pathname }: { pathname: string }) {
  const crumbs = [
    { to: '/', label: es.nav.enterpriseAi, end: true },
    ...(pathname.startsWith('/dashboard')
      ? [{ to: '/dashboard', label: es.nav.executiveDashboard, end: true }]
      : []),
    ...(pathname.startsWith('/financiero')
      ? [{ to: '/financiero', label: es.nav.financialSimulator, end: true }]
      : []),
  ]

  return (
    <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-1.5 text-[11px]">
      {crumbs.map((crumb, index) => (
        <span key={crumb.to} className="inline-flex items-center gap-1.5">
          {index > 0 && <span className="text-muted-light">/</span>}
          <NavLink
            to={crumb.to}
            end={crumb.end}
            className={({ isActive }) =>
              isActive
                ? 'font-semibold text-olnatura-700'
                : 'text-muted hover:text-foreground/80'
            }
          >
            {crumb.label}
          </NavLink>
        </span>
      ))}
    </nav>
  )
}

function ContextChips({
  context,
}: {
  context: ReturnType<typeof useEnterpriseExperience>['context']
}) {
  const chips = [
    context.period ? `${es.experience.period}: ${context.period}` : null,
    context.scenario ? `${es.experience.scenario}: ${context.scenario}` : null,
    context.company ? `${es.experience.company}: ${context.company}` : null,
  ].filter(Boolean)

  if (chips.length === 0) return null

  return (
    <div className="flex flex-wrap gap-2">
      {chips.map((chip) => (
        <span
          key={chip}
          className="rounded-full border border-olnatura-200/70 bg-olnatura-50 px-3 py-1 text-[11px] font-medium text-olnatura-700"
        >
          {chip}
        </span>
      ))}
    </div>
  )
}

export function EnterpriseSidebarNav() {
  const showDebug = isDebugNavVisible()

  return (
    <>
      <aside className="executive-sidebar hidden h-full w-[15rem] shrink-0 flex-col border-r border-border-subtle bg-surface-elevated/95 px-4 py-6 md:flex">
        <Brand />
        <nav className="mt-8 flex flex-1 flex-col gap-1">
          <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-light">
            {es.nav.mainSection}
          </p>
          {EXECUTIVE_NAV.map((item) => (
            <SidebarLink key={item.to} {...item} />
          ))}
          {showDebug && (
            <div className="mt-8 border-t border-border-subtle pt-6">
              <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-amber-700/80">
                {es.nav.debugSection}
              </p>
              <div className="max-h-[40vh] space-y-0.5 overflow-y-auto pr-1">
                {DEBUG_NAV.map((item) => (
                  <SidebarLink key={item.to} to={item.to} label={item.label} compact />
                ))}
              </div>
            </div>
          )}
        </nav>
      </aside>
      <header className="flex items-center justify-between border-b border-border-subtle bg-surface-elevated px-4 py-3 md:hidden">
        <Brand compact />
      </header>
      <nav className="flex gap-1 overflow-x-auto border-b border-border-subtle bg-surface-elevated px-3 py-2 md:hidden">
        {EXECUTIVE_NAV.map((item) => (
          <SidebarLink key={item.to} {...item} mobile />
        ))}
      </nav>
    </>
  )
}

function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className={compact ? 'flex items-center gap-2' : ''}>
      <img
        src="/olnat-logo.png"
        alt="Olnatura"
        className={compact ? 'h-7 w-auto object-contain' : 'h-9 w-auto object-contain object-left'}
      />
      {!compact && (
        <div className="mt-4">
          <p className="text-[13px] font-semibold tracking-[-0.02em] text-foreground">
            Olnatura Intelligence
          </p>
          <p className="mt-1 text-[11px] leading-4 text-muted">{es.experience.platformUnified}</p>
        </div>
      )}
    </div>
  )
}

function SidebarLink({
  to,
  label,
  end = false,
  mobile = false,
  compact = false,
}: {
  to: string
  label: string
  end?: boolean
  mobile?: boolean
  compact?: boolean
}) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        [
          'transition-premium rounded-xl font-medium',
          mobile ? 'shrink-0 px-3 py-2 text-[11px]' : compact ? 'px-2 py-1.5 text-[11px]' : 'px-3 py-2.5 text-[13px]',
          isActive
            ? 'bg-olnatura-600 text-white shadow-[var(--shadow-soft)]'
            : 'text-muted hover:bg-surface-subtle hover:text-foreground/85',
        ].join(' ')
      }
    >
      {label}
    </NavLink>
  )
}

interface EnterpriseShellProps {
  screen: ExperienceScreen
  title: string
  subtitle?: string
  children: ReactNode
  footer?: ReactNode
  fullBleed?: boolean
}

export function EnterpriseShell({
  screen,
  title,
  subtitle,
  children,
  footer,
  fullBleed = false,
}: EnterpriseShellProps) {
  const { recordScreenView } = useEnterpriseExperience()

  useEffect(() => {
    recordScreenView(screen)
  }, [recordScreenView, screen])

  return (
    <div className="flex h-full min-h-0 flex-col bg-[linear-gradient(180deg,var(--color-surface)_0%,var(--color-surface-subtle)_100%)]">
      <EnterpriseUnifiedHeader title={title} subtitle={subtitle} />
      <div className={`min-h-0 flex-1 overflow-y-auto ${fullBleed ? '' : 'executive-page'}`}>
        {children}
      </div>
      {footer}
    </div>
  )
}
