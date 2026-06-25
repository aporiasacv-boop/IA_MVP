import { useEffect, useRef } from 'react'

export function useScrollToBottom(deps: unknown[]) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const node = containerRef.current
    if (!node) return
    node.scrollTop = node.scrollHeight
  }, deps)

  return containerRef
}
