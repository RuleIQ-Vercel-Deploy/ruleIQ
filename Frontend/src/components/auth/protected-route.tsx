"use client"

import type React from "react"
import { Navigate, useLocation } from "react-router-dom"
import { useAuthStore } from "@/store/auth-store"
import { AuthGuard } from "@/components/auth/auth-guard"
import { LoadingLayout } from "@/components/layout/loading-layout"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Shield, AlertTriangle } from "lucide-react"
import { useState, useEffect } from "react"

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredPermissions?: string[]
  requiredRole?: string
  fallback?: React.ReactNode
  redirectTo?: string
}

export function ProtectedRoute({
  children,
  requiredPermissions = [],
  requiredRole,
  fallback,
  redirectTo = "/login",
}: ProtectedRouteProps) {
  const { accessToken, user, isAuthenticated } = useAuthStore()
  const location = useLocation()
  const [isChecking, setIsChecking] = useState(true)
  const [hasPermission, setHasPermission] = useState(false)

  useEffect(() => {
    const checkPermissions = () => {
      setIsChecking(true)

      // Check if user is authenticated
      if (!isAuthenticated || !accessToken) {
        setHasPermission(false)
        setIsChecking(false)
        return
      }

      // Check role-based access
      if (requiredRole && user?.role !== requiredRole) {
        setHasPermission(false)
        setIsChecking(false)
        return
      }

      // Check permission-based access
      if (requiredPermissions.length > 0) {
        const userPermissions = user?.permissions || []
        const hasAllPermissions = requiredPermissions.every((permission) => userPermissions.includes(permission))

        if (!hasAllPermissions) {
          setHasPermission(false)
          setIsChecking(false)
          return
        }
      }

      setHasPermission(true)
      setIsChecking(false)
    }

    checkPermissions()
  }, [isAuthenticated, accessToken, user, requiredPermissions, requiredRole])

  // Show loading state while checking permissions
  if (isChecking) {
    return <LoadingLayout />
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !accessToken) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />
  }

  // Show access denied if user doesn't have required permissions
  if (!hasPermission) {
    if (fallback) {
      return <>{fallback}</>
    }

    return <AccessDenied requiredRole={requiredRole} requiredPermissions={requiredPermissions} />
  }

  // Wrap children in AuthGuard for additional security
  return <AuthGuard>{children}</AuthGuard>
}

// Access denied component
function AccessDenied({
  requiredRole,
  requiredPermissions,
}: {
  requiredRole?: string
  requiredPermissions?: string[]
}) {
  const { logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    window.location.href = "/login"
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50 dark:bg-gray-900">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-12 h-12 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-4">
            <Shield className="h-6 w-6 text-red-600 dark:text-red-400" />
          </div>
          <CardTitle className="text-xl">Access Denied</CardTitle>
          <CardDescription>You don't have permission to access this page.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {requiredRole && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>Required role: {requiredRole}</AlertDescription>
            </Alert>
          )}

          {requiredPermissions && requiredPermissions.length > 0 && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>Required permissions: {requiredPermissions.join(", ")}</AlertDescription>
            </Alert>
          )}

          <div className="flex flex-col sm:flex-row gap-2">
            <Button onClick={() => window.history.back()} variant="outline" className="flex-1">
              Go Back
            </Button>
            <Button onClick={handleLogout} className="flex-1">
              Sign Out
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
