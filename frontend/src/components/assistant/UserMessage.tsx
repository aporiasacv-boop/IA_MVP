interface UserMessageProps {
  content: string
}

export function UserMessage({ content }: UserMessageProps) {
  return (
    <div className="animate-fade-in-up py-4 md:py-5">
      <p className="text-[15px] font-medium leading-7 text-foreground md:text-base md:leading-8">
        {content}
      </p>
    </div>
  )
}
