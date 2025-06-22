"use client"

import { useState, useCallback, useRef, useEffect } from "react"

interface LoadingState {
  isLoading: boolean
  progress: number
  message: string
  error: string | null
}

interface UseLoadingStateOptions {
  initialMessage?: string
  showProgress?: boolean
  minLoadingTime?: number
}

export function useLoadingState(options: UseLoadingStateOptions = {}) {
  const { initialMessage = "Loading...", showProgress = false, minLoadingTime = 0 } = options

  const [state, setState] = useState<LoadingState>({
    isLoading: false,
    progress: 0,
    message: initialMessage,
    error: null,
  })

  const startTimeRef = useRef<number>(0)
  const timeoutRef = useRef<NodeJS.Timeout>()

  const startLoading = useCallback(
    (message?: string) => {
      startTimeRef.current = Date.now()
      setState({
        isLoading: true,
        progress: 0,
        message: message || initialMessage,
        error: null,
      })
    },
    [initialMessage],
  )

  const updateProgress = useCallback((progress: number, message?: string) => {
    setState((prev) => ({
      ...prev,
      progress: Math.max(0, Math.min(100, progress)),
      message: message || prev.message,
    }))
  }, [])

  const updateMessage = useCallback((message: string) => {
    setState((prev) => ({
      ...prev,
      message,
    }))
  }, [])

  const setError = useCallback((error: string) => {
    setState((prev) => ({
      ...prev,
      error,
      isLoading: false,
    }))
  }, [])

  const stopLoading = useCallback(() => {
    const elapsedTime = Date.now() - startTimeRef.current
    const remainingTime = Math.max(0, minLoadingTime - elapsedTime)

    if (remainingTime > 0) {
      timeoutRef.current = setTimeout(() => {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          progress: 100,
        }))
      }, remainingTime)
    } else {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        progress: 100,
      }))
    }
  }, [minLoadingTime])

  const reset = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setState({
      isLoading: false,
      progress: 0,
      message: initialMessage,
      error: null,
    })
  }, [initialMessage])

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return {
    ...state,
    startLoading,
    stopLoading,
    updateProgress,
    updateMessage,
    setError,
    reset,
  }
}

// Hook for async operations with loading states
export function useAsyncOperation<T = any>() {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const execute = useCallback(async (asyncFn: () => Promise<T>) => {
    setIsLoading(true)
    setError(null)

    try {
      const result = await asyncFn()
      setData(result)
      return result
    } catch (err) {
      const error = err instanceof Error ? err : new Error("An error occurred")
      setError(error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setData(null)
    setError(null)
    setIsLoading(false)
  }, [])

  return {
    data,
    error,
    isLoading,
    execute,
    reset,
  }
}
