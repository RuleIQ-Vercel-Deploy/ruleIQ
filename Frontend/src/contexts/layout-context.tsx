"use client"

import type React from "react"
import { createContext, useContext, useState, useCallback } from "react"

interface LayoutContextType {
  sidebarCollapsed: boolean
  setSidebarCollapsed: (collapsed: boolean) => void
  toggleSidebar: () => void
  pageTitle: string
  setPageTitle: (title: string) => void
  breadcrumbs: Array<{ label: string; href?: string }>
  setBreadcrumbs: (breadcrumbs: Array<{ label: string; href?: string }>) => void
}

const LayoutContext = createContext<LayoutContextType | undefined>(undefined)

export function LayoutProvider({ children }: { children: React.ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [pageTitle, setPageTitle] = useState("")
  const [breadcrumbs, setBreadcrumbs] = useState<Array<{ label: string; href?: string }>>([])

  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((prev) => !prev)
  }, [])

  const value: LayoutContextType = {
    sidebarCollapsed,
    setSidebarCollapsed,
    toggleSidebar,
    pageTitle,
    setPageTitle,
    breadcrumbs,
    setBreadcrumbs,
  }

  return <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>
}

export function useLayout() {
  const context = useContext(LayoutContext)
  if (context === undefined) {
    throw new Error("useLayout must be used within a LayoutProvider")
  }
  return context
}
