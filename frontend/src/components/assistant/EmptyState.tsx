import { es } from '../../i18n/spanish'

export function EmptyState() {
  return (
    <div className="animate-fade-in-up flex flex-col items-center justify-center px-4 py-14 text-center md:py-20">
      <div className="rounded-2xl border border-border-subtle bg-surface-elevated px-8 py-10 shadow-[var(--shadow-soft)] md:px-12 md:py-12">
        <img
          src="/olnat-logo.png"
          alt="Olnatura"
          className="mx-auto h-12 w-auto object-contain opacity-95 md:h-14"
        />
        <p className="mt-6 text-[11px] font-semibold uppercase tracking-[0.2em] text-olnatura-600">
          {es.executive.ai.eyebrow}
        </p>
        <h2 className="mt-3 text-xl font-semibold tracking-[-0.03em] text-foreground md:text-2xl">
          {es.executive.ai.emptyTitle}
        </h2>
        <p className="mx-auto mt-4 max-w-md text-[14px] leading-7 text-muted md:text-[15px]">
          {es.executive.ai.emptySubtitle}
        </p>
        <p className="mt-4 text-[13px] text-muted-light">{es.executive.ai.emptyPrompt}</p>
      </div>
    </div>
  )
}
