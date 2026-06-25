import { useEffect, useRef, useState, type FormEvent } from 'react'

interface ChatInputProps {
  onSend: (question: string) => void
  submitDisabled?: boolean
}

export function ChatInput({ onSend, submitDisabled = false }: ChatInputProps) {
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const wasSubmitDisabledRef = useRef(submitDisabled)

  useEffect(() => {
    if (wasSubmitDisabledRef.current && !submitDisabled) {
      inputRef.current?.focus()
    }
    wasSubmitDisabledRef.current = submitDisabled
  }, [submitDisabled])

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (!value.trim() || submitDisabled) return
    onSend(value)
    setValue('')
    requestAnimationFrame(() => {
      inputRef.current?.focus()
    })
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto w-full max-w-3xl">
      <div
        className={[
          'transition-premium flex items-center gap-3 rounded-2xl border bg-surface-elevated px-4 py-3.5 md:px-5 md:py-4',
          focused
            ? 'border-olnatura-500/30 shadow-[var(--shadow-input-focus)]'
            : 'border-border shadow-[var(--shadow-input)] hover:border-olnatura-200',
        ].join(' ')}
      >
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="¿Qué quieres saber sobre tu negocio?"
          className="min-w-0 flex-1 bg-transparent text-[15px] text-foreground outline-none placeholder:text-muted-light"
        />
        <button
          type="submit"
          disabled={submitDisabled || !value.trim()}
          className="transition-premium shrink-0 rounded-xl bg-olnatura-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-olnatura-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Enviar
        </button>
      </div>
    </form>
  )
}
