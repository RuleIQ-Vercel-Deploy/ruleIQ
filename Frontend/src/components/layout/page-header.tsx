"use client"

import type React from "react"
import { BreadcrumbNavigation } from "./breadcrumb-navigation"
import { cn } from "@/lib/utils"

interface PageHeaderProps {
  title: string
  description?: string
  children?: React.ReactNode
  actions?: React.ReactNode
  breadcrumbs?: Array<{ label: string; href?: string; current?: boolean }>
  className?: string
}

export function PageHeader({ title, description, children, actions, breadcrumbs, className }: PageHeaderProps) {
  return (
    <div className={cn("space-y-4 pb-6", className)}>
      {/* Breadcrumbs - Temporarily disabled */}
      {/* <BreadcrumbNavigation items={breadcrumbs} /> */}

      {/* Header content */}
      <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-100">{title}</h1>
          {description && <p className="text-gray-600 dark:text-gray-400">{description}</p>}
        </div>

        {actions && <div className="flex items-center space-x-2">{actions}</div>}
      </div>

      {children}
    </div>
  )
}
