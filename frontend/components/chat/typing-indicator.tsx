export function TypingIndicator() {
  return (
    <div className="flex items-start gap-4">
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-midnight-blue text-gold font-bold text-sm flex-shrink-0">
        IQ
      </div>
      <div className="max-w-lg rounded-xl p-3 bg-eggshell-white text-midnight-blue rounded-bl-none">
        <div className="flex items-center gap-1">
          <span className="h-2 w-2 animate-pulse rounded-full bg-midnight-blue/40 delay-0" />
          <span className="h-2 w-2 animate-pulse rounded-full bg-midnight-blue/40 delay-150" />
          <span className="h-2 w-2 animate-pulse rounded-full bg-midnight-blue/40 delay-300" />
        </div>
      </div>
    </div>
  )
}
