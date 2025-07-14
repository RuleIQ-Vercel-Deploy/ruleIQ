import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { Loader2 } from "lucide-react"
import * as React from "react"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-600 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        primary: "bg-teal-600 text-white shadow-sm hover:bg-teal-700 hover:shadow-md",
        secondary: "bg-white border border-neutral-200 text-neutral-700 hover:bg-neutral-50 hover:border-neutral-300",
        ghost: "text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900",
        destructive: "bg-error-500 text-white shadow-sm hover:bg-error-600 hover:shadow-md",
        link: "text-teal-600 underline-offset-4 hover:underline hover:text-teal-700",
        outline: "border border-teal-600 text-teal-600 hover:bg-teal-50 hover:text-teal-700",
        // Legacy mappings
        default: "bg-teal-600 text-white shadow-sm hover:bg-teal-700 hover:shadow-md",
        turquoise: "bg-teal-600 text-white shadow-sm hover:bg-teal-700 hover:shadow-md",
      },
      size: {
        default: "h-10 px-4 py-2 text-sm",
        sm: "h-8 px-3 text-xs",
        lg: "h-12 px-6 py-3 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading = false, children, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={loading || disabled}
        aria-busy={loading}
        {...props}
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin text-current" aria-hidden="true" />
            <span className="sr-only">Loading</span>
            {children}
          </>
        ) : (
          children
        )}
      </Comp>
    )
  },
)
Button.displayName = "Button"

export { Button, buttonVariants }
