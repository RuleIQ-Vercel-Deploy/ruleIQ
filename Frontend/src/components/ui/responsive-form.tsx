"use client"

import type * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useResponsive } from "@/hooks/use-responsive"
import { cn } from "@/lib/utils"

interface ResponsiveFormProps {
  title?: string
  description?: string
  children: React.ReactNode
  actions?: React.ReactNode
  onSubmit?: (e: React.FormEvent) => void
  loading?: boolean
  className?: string
}

export function ResponsiveForm({
  title,
  description,
  children,
  actions,
  onSubmit,
  loading = false,
  className,
}: ResponsiveFormProps) {
  const { isMobile } = useResponsive()

  return (
    <Card className={cn("w-full max-w-4xl mx-auto", isMobile && "mx-2 max-w-none", className)}>
      {(title || description) && (
        <CardHeader className={cn(isMobile && "px-4 py-4")}>
          {title && <CardTitle className={cn("text-2xl font-bold", isMobile && "text-xl")}>{title}</CardTitle>}
          {description && <CardDescription className={cn(isMobile && "text-sm")}>{description}</CardDescription>}
        </CardHeader>
      )}
      <CardContent className={cn(isMobile && "px-4 pb-4")}>
        <form onSubmit={onSubmit} className="space-y-6">
          <div className={cn("grid gap-6", isMobile ? "grid-cols-1" : "grid-cols-1 md:grid-cols-2")}>{children}</div>
          {actions && (
            <div className={cn("flex justify-end space-x-4 pt-6 border-t", isMobile && "flex-col space-x-0 space-y-3")}>
              {actions}
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  )
}

interface ResponsiveFormFieldProps {
  children: React.ReactNode
  className?: string
  fullWidth?: boolean
}

export function ResponsiveFormField({ children, className, fullWidth = false }: ResponsiveFormFieldProps) {
  const { isMobile } = useResponsive()

  return (
    <div className={cn("space-y-2", fullWidth && "md:col-span-2", isMobile && "col-span-1", className)}>{children}</div>
  )
}
