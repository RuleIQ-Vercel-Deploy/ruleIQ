import { cn } from "@/lib/utils"

import type React from "react"

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-lg",
        // New design system skeleton
        "bg-neutral-200",
        className,
      )}
      {...props}
    />
  )
}

export { Skeleton }
