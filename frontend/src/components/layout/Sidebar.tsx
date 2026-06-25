import { NavLink } from 'react-router-dom'
import { es } from '../../i18n/spanish'

const navItems = [
  { to: '/', label: es.nav.assistant, end: true },
  { to: '/rendimiento', label: es.nav.performance, end: false },
  { to: '/analytics', label: es.nav.analytics, end: false },
  { to: '/audit', label: es.nav.audit, end: false },
  { to: '/entidades', label: es.nav.entities, end: false },
  { to: '/canonicas', label: es.nav.canonical, end: false },
  { to: '/perfiles', label: es.nav.profiles, end: false },
  { to: '/ontologia', label: es.nav.ontology, end: false },
  { to: '/conocimiento', label: es.nav.knowledge, end: false },
  { to: '/razonamiento', label: es.nav.reasoning, end: false },
  { to: '/intencion-semantica', label: es.nav.semanticIntent, end: false },
  { to: '/evidencia', label: es.nav.evidence, end: false },
  { to: '/costos-ia', label: es.nav.aiCosts, end: false },
]

export function Sidebar() {
  return (
    <>
      <aside className="hidden h-full w-[13.5rem] shrink-0 flex-col border-r border-border-subtle bg-surface-elevated/80 px-3 py-5 md:flex">
        <img
          src="/olnat-logo.png"
          alt="Olnatura"
          className="h-9 w-auto object-contain object-left"
        />
        <PlatformStatus />
        <nav className="mt-6 flex flex-col gap-0.5">
          {navItems.map((item) => (
            <SidebarLink key={item.to} {...item} />
          ))}
        </nav>
      </aside>

      <header className="flex items-center justify-between border-b border-border-subtle bg-surface-elevated px-4 py-3 md:hidden">
        <img src="/olnat-logo.png" alt="Olnatura" className="h-7 w-auto object-contain" />
        <PlatformStatus compact />
      </header>
      <nav className="flex border-b border-border-subtle bg-surface-elevated px-3 py-2 md:hidden">
        {navItems.map((item) => (
          <SidebarLink key={item.to} {...item} mobile />
        ))}
      </nav>
    </>
  )
}

function PlatformStatus({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`flex items-center gap-1.5 ${compact ? '' : 'mt-4'}`}>
      <span className="inline-flex h-1.5 w-1.5 rounded-full bg-olnatura-lime" />
      <span className="text-[10px] text-muted-light">{es.nav.platformActive}</span>
    </div>
  )
}

function SidebarLink({
  to,
  label,
  end,
  mobile = false,
}: {
  to: string
  label: string
  end: boolean
  mobile?: boolean
}) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        [
          'transition-premium rounded-lg text-[12px] font-medium',
          mobile ? 'flex-1 px-2 py-2 text-center' : 'px-2.5 py-2',
          isActive
            ? 'bg-olnatura-50 text-olnatura-700'
            : 'text-muted hover:bg-surface-subtle hover:text-foreground/80',
        ].join(' ')
      }
    >
      {label}
    </NavLink>
  )
}
