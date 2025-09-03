export function TypingIndicator() {
  return (
    <div className="flex items-start gap-4">
      <div className="bg-midnight-blue flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold text-gold">
        IQ
      </div>
      <div className="bg-eggshell-white text-midnight-blue max-w-lg rounded-xl rounded-bl-none p-3">
        <div className="flex items-center gap-1">
          <span className="bg-midnight-blue/40 h-2 w-2 animate-pulse rounded-full delay-0" />
          <span className="bg-midnight-blue/40 h-2 w-2 animate-pulse rounded-full delay-150" />
          <span className="bg-midnight-blue/40 h-2 w-2 animate-pulse rounded-full delay-300" />
        </div>
      </div>
    </div>
  );
}
