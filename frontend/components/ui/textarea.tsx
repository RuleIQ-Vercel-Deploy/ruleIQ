import * as React from "react"

import { cn } from "@/lib/utils"

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean
  success?: boolean
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, success, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          "flex min-h-[80px] w-full rounded-lg border bg-white px-4 py-3 text-sm placeholder:text-neutral-400 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200 resize-none",
          // Default state with new design system
          "border-neutral-200",
          // Focus state with teal accent
          "focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600",
          // Error state
          error && "border-red-500 focus:ring-red-500/20 focus:border-red-500",
          // Success state
          success && "border-green-500 focus:ring-green-500/20 focus:border-green-500",
          className,
        )}
        ref={ref}
        {...props}
      />
    )
  },
)
Textarea.displayName = "Textarea"

export { Textarea }
