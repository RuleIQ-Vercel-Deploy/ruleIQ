import { useEffect, useRef, useState } from "react"

interface AccessibilityOptions {
  announceChanges?: boolean
  focusManagement?: boolean
  keyboardNavigation?: boolean
}

export function useAccessibility(options: AccessibilityOptions = {}) {
  const {
    announceChanges = true,
    focusManagement = true,
    keyboardNavigation = true,
  } = options

  const [announcements, setAnnouncements] = useState<string[]>([])
  const announcementRef = useRef<HTMLDivElement>(null)

  const announce = (message: string) => {
    if (!announceChanges) return
    
    setAnnouncements(prev => [...prev, message])
    
    // Clear announcement after a delay
    setTimeout(() => {
      setAnnouncements(prev => prev.slice(1))
    }, 1000)
  }

  const focusElement = (selector: string | HTMLElement) => {
    if (!focusManagement) return

    const element = typeof selector === "string" 
      ? document.querySelector(selector) as HTMLElement
      : selector

    if (element) {
      element.focus()
    }
  }

  const trapFocus = (containerRef: React.RefObject<HTMLElement>) => {
    if (!focusManagement) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return

      const container = containerRef.current
      if (!container) return

      const focusableElements = container.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      ) as NodeListOf<HTMLElement>

      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement.focus()
        }
      }
    }

    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }

  const handleKeyboardNavigation = (
    e: React.KeyboardEvent,
    onEnter?: () => void,
    onEscape?: () => void,
    onArrowUp?: () => void,
    onArrowDown?: () => void
  ) => {
    if (!keyboardNavigation) return

    switch (e.key) {
      case "Enter":
        onEnter?.()
        break
      case "Escape":
        onEscape?.()
        break
      case "ArrowUp":
        e.preventDefault()
        onArrowUp?.()
        break
      case "ArrowDown":
        e.preventDefault()
        onArrowDown?.()
        break
    }
  }

  // Create screen reader announcement area
  useEffect(() => {
    if (!announceChanges) return

    const announcementArea = document.createElement("div")
    announcementArea.setAttribute("aria-live", "polite")
    announcementArea.setAttribute("aria-atomic", "true")
    announcementArea.style.position = "absolute"
    announcementArea.style.left = "-10000px"
    announcementArea.style.width = "1px"
    announcementArea.style.height = "1px"
    announcementArea.style.overflow = "hidden"
    
    document.body.appendChild(announcementArea)

    return () => {
      document.body.removeChild(announcementArea)
    }
  }, [announceChanges])

  return {
    announce,
    focusElement,
    trapFocus,
    handleKeyboardNavigation,
    announcements,
  }
}
