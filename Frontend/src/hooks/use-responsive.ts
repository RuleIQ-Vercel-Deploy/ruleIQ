"use client"

import { useState, useEffect } from "react"

export type Breakpoint = "sm" | "md" | "lg" | "xl" | "2xl"

export interface BreakpointValues {
  sm: boolean
  md: boolean
  lg: boolean
  xl: boolean
  "2xl": boolean
}

export function useResponsive() {
  const [breakpoints, setBreakpoints] = useState<BreakpointValues>({
    sm: false,
    md: false,
    lg: false,
    xl: false,
    "2xl": false,
  })

  const [isMobile, setIsMobile] = useState(false)
  const [isTablet, setIsTablet] = useState(false)
  const [isDesktop, setIsDesktop] = useState(false)

  useEffect(() => {
    const updateBreakpoints = () => {
      const width = window.innerWidth

      const newBreakpoints = {
        sm: width >= 640,
        md: width >= 768,
        lg: width >= 1024,
        xl: width >= 1280,
        "2xl": width >= 1536,
      }

      setBreakpoints(newBreakpoints)
      setIsMobile(width < 768)
      setIsTablet(width >= 768 && width < 1024)
      setIsDesktop(width >= 1024)
    }

    updateBreakpoints()
    window.addEventListener("resize", updateBreakpoints)

    return () => window.removeEventListener("resize", updateBreakpoints)
  }, [])

  return {
    ...breakpoints,
    isMobile,
    isTablet,
    isDesktop,
    breakpoints,
  }
}

export function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const media = window.matchMedia(query)
    if (media.matches !== matches) {
      setMatches(media.matches)
    }

    const listener = () => setMatches(media.matches)
    media.addEventListener("change", listener)

    return () => media.removeEventListener("change", listener)
  }, [matches, query])

  return matches
}
