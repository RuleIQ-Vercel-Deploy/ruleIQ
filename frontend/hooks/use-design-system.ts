'use client';

import { useState, useEffect } from 'react';

interface DesignSystemState {
  designSystem: 'legacy' | 'teal';
  isNewTheme: boolean;
}

export function useDesignSystem() {
  const [state, setState] = useState<DesignSystemState>({
    designSystem: 'teal',
    isNewTheme: true,
  });

  // Load saved preference from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('design-system');
    if (saved && (saved === 'legacy' || saved === 'teal')) {
      setState({
        designSystem: saved,
        isNewTheme: saved === 'teal',
      });
    }
  }, []);

  // Save preference when changed
  useEffect(() => {
    localStorage.setItem('design-system', state.designSystem);
  }, [state.designSystem]);

  const toggleDesignSystem = () => {
    setState(prev => ({
      designSystem: prev.designSystem === 'legacy' ? 'teal' : 'legacy',
      isNewTheme: prev.designSystem === 'legacy',
    }));
  };

  return {
    designSystem: state.designSystem,
    isNewTheme: state.isNewTheme,
    toggleDesignSystem,
  };
}