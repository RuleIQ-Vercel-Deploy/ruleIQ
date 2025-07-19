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
          "flex min-h-[80px] w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50 transition-colors resize-none",
          // Default state
          "border-input focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
          // Focus state using design system colors
          "focus-visible:ring-ring focus-visible:border-ring",
          // Error state
          error && "border-error focus-visible:ring-error focus-visible:border-error",
          // Success state
          success && "border-success focus-visible:ring-success focus-visible:border-success",
          // Remove hardcoded colors - let theme handle it
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
