'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useCallback } from 'react';
import { toast } from 'sonner';

import { useAuthStore } from '@/lib/stores/auth.store';

interface Shortcut {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  metaKey?: boolean;
  action: () => void;
  description: string;
  requiresProfile?: boolean;
}

export function useKeyboardShortcuts() {
  const router = useRouter();
  const { user } = useAuthStore();
  const hasProfile = user?.businessProfile?.id;

  const shortcuts: Shortcut[] = [
    {
      key: 'k',
      metaKey: true,
      action: () => {
        // This will be handled by command palette
        document.dispatchEvent(new CustomEvent('openCommandPalette'));
      },
      description: 'Open command palette',
    },
    {
      key: 'n',
      altKey: true,
      action: () => {
        if (!hasProfile) {
          toast.error('Complete your business profile first');
          return;
        }
        router.push('/assessments/new');
      },
      description: 'New assessment',
      requiresProfile: true,
    },
    {
      key: 'p',
      altKey: true,
      action: () => {
        if (!hasProfile) {
          toast.error('Complete your business profile first');
          return;
        }
        router.push('/policies/generate');
      },
      description: 'Generate policy',
      requiresProfile: true,
    },
    {
      key: 'u',
      altKey: true,
      action: () => {
        router.push('/evidence?action=upload');
      },
      description: 'Upload evidence',
    },
    {
      key: 'i',
      altKey: true,
      action: () => {
        router.push('/chat');
      },
      description: 'Open IQ chat',
    },
    {
      key: 'd',
      altKey: true,
      action: () => {
        router.push('/dashboard');
      },
      description: 'Go to dashboard',
    },
    {
      key: 's',
      altKey: true,
      action: () => {
        router.push('/settings');
      },
      description: 'Open settings',
    },
    {
      key: '?',
      shiftKey: true,
      action: () => {
        // Show keyboard shortcuts help
        document.dispatchEvent(new CustomEvent('showKeyboardShortcuts'));
      },
      description: 'Show keyboard shortcuts',
    },
  ];

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs
      const target = event.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      const matchedShortcut = shortcuts.find((shortcut) => {
        const keyMatches = event.key.toLowerCase() === shortcut.key.toLowerCase();
        const ctrlMatches = shortcut.ctrlKey ? event.ctrlKey : !event.ctrlKey;
        const shiftMatches = shortcut.shiftKey ? event.shiftKey : !event.shiftKey;
        const altMatches = shortcut.altKey ? event.altKey : !event.altKey;
        const metaMatches = shortcut.metaKey ? event.metaKey : !event.metaKey;

        return keyMatches && ctrlMatches && shiftMatches && altMatches && metaMatches;
      });

      if (matchedShortcut) {
        event.preventDefault();
        matchedShortcut.action();
      }
    },
    [shortcuts, hasProfile],
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return shortcuts;
}

export function getShortcutDisplay(shortcut: Shortcut): string {
  const keys = [];

  if (shortcut.metaKey) keys.push('⌘');
  if (shortcut.ctrlKey) keys.push('Ctrl');
  if (shortcut.altKey) keys.push('Alt');
  if (shortcut.shiftKey) keys.push('Shift');
  keys.push(shortcut.key.toUpperCase());

  return keys.join('+');
}
