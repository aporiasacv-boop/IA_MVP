import { es } from '../../i18n/spanish'

const SECTIONS = [
  { title: es.performance.whyFaster, body: es.performance.whyFasterBody },
  { title: es.performance.whyLessTokens, body: es.performance.whyLessTokensBody },
  { title: es.performance.whyNotAllLlm, body: es.performance.whyNotAllLlmBody },
  { title: es.performance.whyIntermediateLayers, body: es.performance.whyIntermediateLayersBody },
]

export function ArchitecturalExplanation() {
  return (
    <section className="border-t border-border-subtle px-4 py-10 md:px-8 md:py-12">
      <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
        {es.performance.architecturalEyebrow}
      </p>
      <h2 className="mt-3 text-lg font-semibold text-foreground md:text-xl">
        {es.performance.architecturalTitle}
      </h2>

      <div className="mt-8 space-y-6">
        {SECTIONS.map((section) => (
          <article
            key={section.title}
            className="transition-premium rounded-xl border border-border-subtle bg-surface-elevated px-5 py-5 hover:border-olnatura-100"
          >
            <h3 className="text-[15px] font-medium text-olnatura-700">{section.title}</h3>
            <p className="mt-2 text-[14px] leading-7 text-muted">{section.body}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
