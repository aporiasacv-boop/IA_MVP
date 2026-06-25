export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center px-4 py-16 text-center md:py-20">
      <img
        src="/olnat-logo.png"
        alt="Olnatura"
        className="h-14 w-auto object-contain opacity-95 md:h-16"
      />
      <h1 className="mt-8 text-xl font-semibold tracking-[-0.02em] text-foreground md:text-2xl">
        Asistente de Inteligencia Empresarial
      </h1>
      <p className="mt-3 max-w-md text-[14px] leading-6 text-muted md:text-[15px] md:leading-7">
        Pregunta, analiza y descubre información clave de tu negocio.
      </p>
    </div>
  )
}
