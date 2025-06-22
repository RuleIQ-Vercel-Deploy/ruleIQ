import { useCallback, useRef, useState, useEffect } from "react"

interface PerformanceMetrics {
  renderTime: number
  componentCount: number
  memoryUsage?: number
  lastUpdate: number
}

export function usePerformance(componentName?: string) {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    componentCount: 0,
    lastUpdate: Date.now(),
  })
  
  const renderStartRef = useRef<number>(0)
  const renderCountRef = useRef<number>(0)

  const startMeasure = useCallback(() => {
    renderStartRef.current = performance.now()
  }, [])

  const endMeasure = useCallback(() => {
    const renderTime = performance.now() - renderStartRef.current
    renderCountRef.current += 1

    setMetrics(prev => ({
      ...prev,
      renderTime,
      componentCount: renderCountRef.current,
      lastUpdate: Date.now(),
      memoryUsage: (performance as any).memory?.usedJSHeapSize || undefined,
    }))

    if (componentName && renderTime > 16) { // > 16ms is slow
      console.warn(`Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`)
    }
  }, [componentName])

  const measureRender = useCallback((fn: () => void) => {
    startMeasure()
    fn()
    endMeasure()
  }, [startMeasure, endMeasure])

  // Auto-measure on mount
  useEffect(() => {
    startMeasure()
    return () => {
      endMeasure()
    }
  }, [startMeasure, endMeasure])

  return {
    metrics,
    startMeasure,
    endMeasure,
    measureRender,
  }
}
