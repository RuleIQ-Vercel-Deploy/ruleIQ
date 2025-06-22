import { useState, useCallback, useRef } from "react"

interface OptimizedStateOptions<T> {
  debounceMs?: number
  throttleMs?: number
  equalityFn?: (a: T, b: T) => boolean
}

export function useOptimizedState<T>(
  initialValue: T,
  options: OptimizedStateOptions<T> = {}
) {
  const { debounceMs = 0, throttleMs = 0, equalityFn } = options
  const [state, setState] = useState<T>(initialValue)
  const timeoutRef = useRef<NodeJS.Timeout>()
  const lastUpdateRef = useRef<number>(0)

  const optimizedSetState = useCallback(
    (newValue: T | ((prev: T) => T)) => {
      const now = Date.now()
      const actualNewValue = typeof newValue === "function" 
        ? (newValue as (prev: T) => T)(state) 
        : newValue

      // Check equality if provided
      if (equalityFn && equalityFn(state, actualNewValue)) {
        return
      }

      const updateState = () => {
        setState(actualNewValue)
        lastUpdateRef.current = now
      }

      // Clear existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }

      // Apply throttling
      if (throttleMs > 0 && now - lastUpdateRef.current < throttleMs) {
        return
      }

      // Apply debouncing
      if (debounceMs > 0) {
        timeoutRef.current = setTimeout(updateState, debounceMs)
      } else {
        updateState()
      }
    },
    [state, debounceMs, throttleMs, equalityFn]
  )

  return [state, optimizedSetState] as const
}
