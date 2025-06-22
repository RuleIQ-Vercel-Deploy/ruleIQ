"use client"

import type React from "react"
import { useAuthStore } from "@/store/auth-store"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Shield } from "lucide-react"

interface PermissionGuardProps {
  children: React.ReactNode
  requiredPermissions: string[]
  requireAll?: boolean
  fallback?: React.ReactNode
  showAlert?: boolean
}

export function PermissionGuard({
  children,
  requiredPermissions,
  requireAll = true,
  fallback,
  showAlert = true,
}: PermissionGuardProps) {
  const { user } = useAuthStore()

  const userPermissions = user?.permissions || []

  const hasPermission = requireAll
    ? requiredPermissions.every((permission) => userPermissions.includes(permission))
    : requiredPermissions.some((permission) => userPermissions.includes(permission))

  if (!hasPermission) {
    if (fallback) {
      return <>{fallback}</>
    }

    if (showAlert) {
      return (
        <Alert variant="destructive">
          <Shield className="h-4 w-4" />
          <AlertDescription>
            You need the following permissions to access this content: {requiredPermissions.join(", ")}
          </AlertDescription>
        </Alert>
      )
    }

    return null
  }

  return <>{children}</>
}
