import { cn } from "@/lib/utils"

import type React from "react"

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md",
        // Custom ruleIQ skeleton color
        "bg-white/10",
        className,
      )}
      {...props}
    />
  )
}

export { Skeleton }
