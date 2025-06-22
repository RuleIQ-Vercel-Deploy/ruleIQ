"use client"

import type React from "react"
import { useAuthStore } from "@/store/auth-store"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Shield } from "lucide-react"

interface RoleGuardProps {
  children: React.ReactNode
  allowedRoles: string[]
  fallback?: React.ReactNode
  showAlert?: boolean
}

export function RoleGuard({ children, allowedRoles, fallback, showAlert = true }: RoleGuardProps) {
  const { user } = useAuthStore()

  const hasRequiredRole = user?.role && allowedRoles.includes(user.role)

  if (!hasRequiredRole) {
    if (fallback) {
      return <>{fallback}</>
    }

    if (showAlert) {
      return (
        <Alert variant="destructive">
          <Shield className="h-4 w-4" />
          <AlertDescription>
            You need one of the following roles to access this content: {allowedRoles.join(", ")}
          </AlertDescription>
        </Alert>
      )
    }

    return null
  }

  return <>{children}</>
}
