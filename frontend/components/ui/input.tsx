import * as React from "react"

import { cn } from "@/lib/utils"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
  success?: boolean
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, type, error, success, ...props }, ref) => {
  return (
    <>
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-lg border bg-white px-3 py-2 text-sm placeholder:text-neutral-400 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200",
          // Default state with new design system
          "border-neutral-200",
          // Focus state with teal accent
          "focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600",
          // Error state
          error && "border-red-500 focus:ring-red-500/20 focus:border-red-500",
          // Success state
          success && "border-green-500 focus:ring-green-500/20 focus:border-green-500",
          // File input styling
          "file:border-0 file:bg-transparent file:text-sm file:font-medium",
          className,
        )}
        ref={ref}
        aria-invalid={error ? "true" : undefined}
        aria-describedby={error && props["aria-describedby"] ? props["aria-describedby"] : undefined}
        {...props}
      />
      {error && !props["aria-describedby"] && (
        <span className="sr-only" role="status" aria-live="assertive">
          Error in input field
        </span>
      )}
    </>
  )
})
Input.displayName = "Input"

export { Input }
