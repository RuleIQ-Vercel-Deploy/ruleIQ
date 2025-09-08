'use client';

import * as React from 'react';
import { env } from '@/config/env';

type DesignSystem = 'legacy' | 'teal';

type DesignSystemProviderProps = {
  children: React.ReactNode;
  forcedSystem?: DesignSystem;
};

type DesignSystemProviderState = {
  designSystem: DesignSystem;
  isNewTheme: boolean;
  toggleDesignSystem: () => void;
};

const initialState: DesignSystemProviderState = {
  designSystem: 'legacy',
  isNewTheme: false,
  toggleDesignSystem: () => null,
};

const DesignSystemProviderContext = React.createContext<DesignSystemProviderState>(initialState);

export function DesignSystemProvider({ children, forcedSystem }: DesignSystemProviderProps) {
  const [designSystem, setDesignSystem] = React.useState<DesignSystem>(() => {
    // Priority: forcedSystem > env flag > localStorage > default
    if (forcedSystem) return forcedSystem;
    if (env.NEXT_PUBLIC_USE_NEW_THEME) return 'teal';

    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('ruleiq-design-system');
      if (stored === 'teal' || stored === 'legacy') return stored;
    }

    return 'legacy';
  });

  React.useEffect(() => {
    const root = window.document.documentElement;

    // Remove existing design system classes
    root.classList.remove('design-legacy', 'design-teal');

    // Add current design system class
    root.classList.add(`design-${designSystem}`);

    // Store preference
    localStorage.setItem('ruleiq-design-system', designSystem);
  }, [designSystem]);

  const value = {
    designSystem,
    isNewTheme: designSystem === 'teal',
    toggleDesignSystem: () => {
      setDesignSystem((current) => (current === 'legacy' ? 'teal' : 'legacy'));
    },
  };

  return (
    <DesignSystemProviderContext.Provider value={value}>
      {children}
    </DesignSystemProviderContext.Provider>
  );
}

export const useDesignSystem = () => {
  const context = React.useContext(DesignSystemProviderContext);

  if (context === undefined) {
    throw new Error('useDesignSystem must be used within a DesignSystemProvider');
  }

  return context;
};
