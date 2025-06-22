"use client"

import type React from "react"

import { useEffect, useCallback, useRef } from "react"
import { useAuthStore } from "@/store/auth-store"
import { authApi } from "@/api/auth"
import { useToast } from "@/hooks/use-toast"
import { Button } from "@/components/ui/button"
import { RefreshCw } from "lucide-react"

interface SessionManagerProps {
  children: React.ReactNode
  sessionTimeout?: number // in minutes
  warningTime?: number // in minutes before timeout
  checkInterval?: number // in milliseconds
}

export function SessionManager({
  children,
  sessionTimeout = 60, // 1 hour
  warningTime = 5, // 5 minutes warning
  checkInterval = 60000, // 1 minute
}: SessionManagerProps) {
  const { accessToken, logout, refreshToken, setUser } = useAuthStore()
  const { toast } = useToast()
  const lastActivityRef = useRef(Date.now())
  const warningShownRef = useRef(false)
  const intervalRef = useRef<NodeJS.Timeout>()

  const updateLastActivity = useCallback(() => {
    lastActivityRef.current = Date.now()
    warningShownRef.current = false
  }, [])

  const handleSessionExpired = useCallback(() => {
    toast({
      variant: "destructive",
      title: "Session Expired",
      description: "Your session has expired. Please sign in again.",
    })
    logout()
    window.location.href = "/login"
  }, [logout, toast])

  const handleSessionWarning = useCallback(() => {
    if (!warningShownRef.current) {
      warningShownRef.current = true
      toast({
        title: "Session Expiring Soon",
        description: `Your session will expire in ${warningTime} minutes. Click to extend.`,
        action: (
          <Button
            size="sm"
            onClick={() => {
              updateLastActivity()
              toast({
                title: "Session Extended",
                description: "Your session has been extended.",
              })
            }}
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Extend
          </Button>
        ),
      })
    }
  }, [warningTime, updateLastActivity, toast])

  const checkSession = useCallback(async () => {
    if (!accessToken) return

    const now = Date.now()
    const timeSinceLastActivity = now - lastActivityRef.current
    const timeoutMs = sessionTimeout * 60 * 1000
    const warningMs = warningTime * 60 * 1000

    // Check if session should expire
    if (timeSinceLastActivity >= timeoutMs) {
      handleSessionExpired()
      return
    }

    // Check if warning should be shown
    if (timeSinceLastActivity >= timeoutMs - warningMs) {
      handleSessionWarning()
    }

    // Try to refresh user data periodically
    try {
      const userData = await authApi.getProfile()
      setUser(userData)
    } catch (error) {
      console.error("Failed to refresh user data:", error)
      // Don't logout immediately, token might still be valid
    }
  }, [accessToken, sessionTimeout, warningTime, handleSessionExpired, handleSessionWarning, setUser])

  // Set up activity listeners
  useEffect(() => {
    const events = ["mousedown", "mousemove", "keypress", "scroll", "touchstart", "click"]

    const handleActivity = () => {
      updateLastActivity()
    }

    events.forEach((event) => {
      document.addEventListener(event, handleActivity, true)
    })

    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleActivity, true)
      })
    }
  }, [updateLastActivity])

  // Set up session check interval
  useEffect(() => {
    if (accessToken) {
      intervalRef.current = setInterval(checkSession, checkInterval)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [accessToken, checkSession, checkInterval])

  return <>{children}</>
}
