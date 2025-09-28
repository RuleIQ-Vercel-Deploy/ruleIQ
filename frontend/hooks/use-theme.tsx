"use client";

import { ThemeProvider as NextThemeProvider, useTheme as useNextTheme } from 'next-themes';

type ThemeProviderProps = React.ComponentProps<typeof NextThemeProvider>;

export const useTheme = () => {
  return useNextTheme();
};

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemeProvider {...props}>{children}</NextThemeProvider>;
}
