"use client"

import { useState, useRef, useCallback } from "react"

export interface TouchPosition {
  x: number
  y: number
}

export interface SwipeDirection {
  direction: "left" | "right" | "up" | "down" | null
  distance: number
}

export function useSwipe(onSwipe?: (direction: SwipeDirection) => void, threshold = 50) {
  const [touchStart, setTouchStart] = useState<TouchPosition | null>(null)
  const [touchEnd, setTouchEnd] = useState<TouchPosition | null>(null)

  const onTouchStart = useCallback((e: TouchEvent) => {
    setTouchEnd(null)
    setTouchStart({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    })
  }, [])

  const onTouchMove = useCallback((e: TouchEvent) => {
    setTouchEnd({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    })
  }, [])

  const onTouchEnd = useCallback(() => {
    if (!touchStart || !touchEnd) return

    const distanceX = touchStart.x - touchEnd.x
    const distanceY = touchStart.y - touchEnd.y
    const isLeftSwipe = distanceX > threshold
    const isRightSwipe = distanceX < -threshold
    const isUpSwipe = distanceY > threshold
    const isDownSwipe = distanceY < -threshold

    let direction: SwipeDirection["direction"] = null
    let distance = 0

    if (isLeftSwipe) {
      direction = "left"
      distance = Math.abs(distanceX)
    } else if (isRightSwipe) {
      direction = "right"
      distance = Math.abs(distanceX)
    } else if (isUpSwipe) {
      direction = "up"
      distance = Math.abs(distanceY)
    } else if (isDownSwipe) {
      direction = "down"
      distance = Math.abs(distanceY)
    }

    if (direction && onSwipe) {
      onSwipe({ direction, distance })
    }
  }, [touchStart, touchEnd, threshold, onSwipe])

  return {
    onTouchStart,
    onTouchMove,
    onTouchEnd,
  }
}

export function useLongPress(onLongPress: () => void, delay = 500) {
  const [isPressed, setIsPressed] = useState(false)
  const timeoutRef = useRef<NodeJS.Timeout>()

  const start = useCallback(() => {
    setIsPressed(true)
    timeoutRef.current = setTimeout(() => {
      onLongPress()
    }, delay)
  }, [onLongPress, delay])

  const stop = useCallback(() => {
    setIsPressed(false)
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
  }, [])

  return {
    onMouseDown: start,
    onMouseUp: stop,
    onMouseLeave: stop,
    onTouchStart: start,
    onTouchEnd: stop,
    isPressed,
  }
}
