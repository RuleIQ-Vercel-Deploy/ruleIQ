'use client'

import { useState, useCallback } from 'react'

type DesignSystem = 'old' | 'new'

interface DesignSystemState {
  designSystem: DesignSystem
  isNewTheme: boolean
  toggleDesignSystem: () => void
}

export function useDesignSystem(): DesignSystemState {
  const [designSystem, setDesignSystem] = useState<DesignSystem>('new')
  
  const toggleDesignSystem = useCallback(() => {
    setDesignSystem(prev => prev === 'old' ? 'new' : 'old')
  }, [])
  
  const isNewTheme = designSystem === 'new'
  
  return {
    designSystem,
    isNewTheme,
    toggleDesignSystem
  }
}