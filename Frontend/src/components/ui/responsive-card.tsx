"use client"

import type * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useResponsive } from "@/hooks/use-responsive"
import { cn } from "@/lib/utils"

interface ResponsiveCardProps extends React.ComponentProps<typeof Card> {
  title?: string
  description?: string
  children?: React.ReactNode
  actions?: React.ReactNode
  mobileLayout?: "stack" | "compact"
  touchOptimized?: boolean
}

export function ResponsiveCard({
  title,
  description,
  children,
  actions,
  mobileLayout = "stack",
  touchOptimized = true,
  className,
  ...props
}: ResponsiveCardProps) {
  const { isMobile } = useResponsive()

  return (
    <Card
      className={cn(
        "transition-all duration-200",
        touchOptimized && "touch-manipulation",
        isMobile && ["mx-2 sm:mx-0", mobileLayout === "compact" && "p-2"],
        className,
      )}
      {...props}
    >
      {(title || description || actions) && (
        <CardHeader
          className={cn("flex flex-row items-center justify-between space-y-0", isMobile && "pb-3 px-4 pt-4")}
        >
          <div className="space-y-1 flex-1 min-w-0">
            {title && (
              <CardTitle className={cn("text-lg font-semibold", isMobile && "text-base truncate")}>{title}</CardTitle>
            )}
            {description && (
              <CardDescription className={cn("text-sm text-muted-foreground", isMobile && "text-xs line-clamp-2")}>
                {description}
              </CardDescription>
            )}
          </div>
          {actions && <div className={cn("flex items-center space-x-2 ml-4", isMobile && "space-x-1")}>{actions}</div>}
        </CardHeader>
      )}
      <CardContent className={cn(isMobile && ["px-4 pb-4", mobileLayout === "compact" && "px-2 pb-2"])}>
        {children}
      </CardContent>
    </Card>
  )
}
