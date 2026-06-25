import type { ReactNode } from 'react'

const MONTHS =
  'enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre'

const ALL_CAPS_ENTITY =
  /\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s&.-]{4,}\b/g

const TOKEN_PATTERN = new RegExp(
  [
    String.raw`\b\d{1,3}(?:,\d{3})+(?:\.\d+)?%?`,
    String.raw`\b\d+(?:\.\d+)?%`,
    String.raw`\b(?:${MONTHS})\b`,
    String.raw`\b20\d{2}\b`,
    String.raw`\b\d+(?:\.\d+)?\s*millones\b`,
  ].join('|'),
  'gi',
)

function classifyToken(token: string): 'metric' | 'highlight' | 'block' {
  const trimmed = token.trim()
  if (
    trimmed.length > 4 &&
    /^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s&.-]+$/.test(trimmed) &&
    trimmed === trimmed.toUpperCase()
  ) {
    return 'block'
  }
  if (/^\d/.test(token) || /%/.test(token) || /millones/i.test(token) || /^20\d{2}$/.test(token)) {
    return 'metric'
  }
  if (new RegExp(`^(${MONTHS})$`, 'i').test(token)) {
    return 'highlight'
  }
  return 'metric'
}

function renderSegment(text: string, keyPrefix: string): ReactNode[] {
  const nodes: ReactNode[] = []
  let lastIndex = 0
  let matchIndex = 0
  const combined = new RegExp(
    `${ALL_CAPS_ENTITY.source}|${TOKEN_PATTERN.source}`,
    'gi',
  )

  for (const match of text.matchAll(combined)) {
    const index = match.index ?? 0
    if (index > lastIndex) {
      nodes.push(text.slice(lastIndex, index))
    }

    const token = match[0]
    const kind = classifyToken(token)

    if (kind === 'block') {
      nodes.push(
        <span key={`${keyPrefix}-${matchIndex}`} className="executive-block-highlight">
          {token.trim()}
        </span>,
      )
    } else {
      const className = kind === 'metric' ? 'executive-metric' : 'executive-highlight'
      nodes.push(
        <span key={`${keyPrefix}-${matchIndex}`} className={className}>
          {token}
        </span>,
      )
    }

    lastIndex = index + token.length
    matchIndex += 1
  }

  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex))
  }

  return nodes.length > 0 ? nodes : [text]
}

interface ExecutiveTextProps {
  content: string
}

export function ExecutiveText({ content }: ExecutiveTextProps) {
  const paragraphs = content.split('\n').filter(Boolean)

  return (
    <div className="space-y-4">
      {paragraphs.map((paragraph, index) => {
        const isBullet = paragraph.startsWith('- ')

        if (isBullet) {
          return (
            <p
              key={`${paragraph}-${index}`}
              className="border-l-2 border-olnatura-200 pl-4 text-[15px] leading-7 text-muted md:text-base md:leading-8"
            >
              {renderSegment(paragraph.slice(2), `p-${index}`)}
            </p>
          )
        }

        return (
          <p
            key={`${paragraph}-${index}`}
            className="text-[17px] leading-8 text-foreground/90 md:text-[19px] md:leading-9"
          >
            {renderSegment(paragraph, `p-${index}`)}
          </p>
        )
      })}
    </div>
  )
}
