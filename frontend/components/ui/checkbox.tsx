"use client"

import * as CheckboxPrimitive from "@radix-ui/react-checkbox"
import { Check } from "lucide-react"
import * as React from "react"

import { cn } from "@/lib/utils"

const Checkbox = React.forwardRef<
  React.ElementRef<typeof CheckboxPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root> & {
    error?: boolean
    success?: boolean
  }
>(({ className, error, success, ...props }, ref) => (
  <CheckboxPrimitive.Root
    ref={ref}
    className={cn(
      "peer h-4 w-4 shrink-0 rounded border bg-white disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200",
      // Ensure minimum 16x16px tap target for accessibility
      "min-h-[16px] min-w-[16px]",
      // Default state with new design system
      "border-neutral-300",
      // Focus state with visible ring
      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500/20 focus-visible:ring-offset-2",
      // Checked state with teal
      "data-[state=checked]:bg-teal-600 data-[state=checked]:border-teal-600 data-[state=checked]:text-white",
      // Error state
      error && "border-red-500 focus-visible:ring-red-500/20 data-[state=checked]:bg-red-500 data-[state=checked]:border-red-500",
      // Success state
      success &&
        "border-green-500 focus-visible:ring-green-500/20 data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500",
      className,
    )}
    aria-invalid={error ? "true" : undefined}
    {...props}
  >
    <CheckboxPrimitive.Indicator className={cn("flex items-center justify-center text-current")}>
      <Check className="h-4 w-4" />
    </CheckboxPrimitive.Indicator>
  </CheckboxPrimitive.Root>
))
Checkbox.displayName = CheckboxPrimitive.Root.displayName

export { Checkbox }
