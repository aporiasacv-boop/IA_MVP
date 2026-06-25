import { es } from '../../i18n/spanish'

export function PerformanceHero() {
  return (
    <section className="mx-auto max-w-4xl px-6 pt-10 pb-2 md:px-12 md:pt-12">
      <p className="text-[11px] font-medium uppercase tracking-[0.22em] text-muted-light">
        {es.nav.performance}
      </p>
      <h1 className="mt-4 text-[1.75rem] font-semibold tracking-[-0.03em] text-foreground md:text-[2rem]">
        {es.performance.heroTitle}
      </h1>
      <p className="mt-4 max-w-2xl text-[15px] leading-7 text-muted md:text-base md:leading-8">
        {es.performance.heroSubtitle}
      </p>
    </section>
  )
}
