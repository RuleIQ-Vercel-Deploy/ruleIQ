"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useAuthStore } from "@/store/auth-store"
import { authApi } from "@/api/auth"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { RefreshCw } from "lucide-react"

interface AuthGuardProps {
  children: React.ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { accessToken, user, setUser, logout } = useAuthStore()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const verifyAuth = async () => {
      if (!accessToken) {
        setIsLoading(false)
        return
      }

      if (user) {
        setIsLoading(false)
        return
      }

      try {
        const userData = await authApi.getProfile()
        setUser(userData)
      } catch (err: any) {
        console.error("Auth verification failed:", err)
        if (err.response?.status === 401) {
          logout()
        } else {
          setError("Failed to verify authentication")
        }
      } finally {
        setIsLoading(false)
      }
    }

    verifyAuth()
  }, [accessToken, user, setUser, logout])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="space-y-4 w-full max-w-md">
          <Skeleton className="h-8 w-3/4 mx-auto" />
          <Skeleton className="h-4 w-1/2 mx-auto" />
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md space-y-4">
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <Button onClick={() => window.location.reload()} className="w-full" variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Try again
          </Button>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
