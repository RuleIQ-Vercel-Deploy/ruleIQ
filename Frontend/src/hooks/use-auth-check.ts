"use client"

import { useEffect, useState } from "react"
import { useAuthStore } from "@/store/auth-store"
import { authApi } from "@/api/auth"

interface AuthCheckOptions {
  redirectOnFailure?: boolean
  redirectTo?: string
  requiredPermissions?: string[]
  requiredRole?: string
}

export function useAuthCheck(options: AuthCheckOptions = {}) {
  const { redirectOnFailure = false, redirectTo = "/login", requiredPermissions = [], requiredRole } = options

  const { accessToken, user, isAuthenticated, logout, setUser } = useAuthStore()
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthorized, setIsAuthorized] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      setIsLoading(true)
      setError(null)

      try {
        // Check if user has access token
        if (!accessToken) {
          setIsAuthorized(false)
          if (redirectOnFailure) {
            window.location.href = redirectTo
          }
          return
        }

        // Verify token and get user data if not available
        if (!user) {
          try {
            const userData = await authApi.getProfile()
            setUser(userData)
          } catch (err) {
            console.error("Failed to get user profile:", err)
            logout()
            setIsAuthorized(false)
            if (redirectOnFailure) {
              window.location.href = redirectTo
            }
            return
          }
        }

        // Check role-based authorization
        if (requiredRole && user?.role !== requiredRole) {
          setIsAuthorized(false)
          setError(`Required role: ${requiredRole}`)
          return
        }

        // Check permission-based authorization
        if (requiredPermissions.length > 0) {
          const userPermissions = user?.permissions || []
          const hasAllPermissions = requiredPermissions.every((permission) => userPermissions.includes(permission))

          if (!hasAllPermissions) {
            setIsAuthorized(false)
            setError(`Required permissions: ${requiredPermissions.join(", ")}`)
            return
          }
        }

        setIsAuthorized(true)
      } catch (err) {
        console.error("Auth check failed:", err)
        setError("Authentication check failed")
        setIsAuthorized(false)
        if (redirectOnFailure) {
          logout()
          window.location.href = redirectTo
        }
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [accessToken, user, requiredPermissions, requiredRole, redirectOnFailure, redirectTo, logout, setUser])

  return {
    isLoading,
    isAuthenticated,
    isAuthorized,
    error,
    user,
  }
}
