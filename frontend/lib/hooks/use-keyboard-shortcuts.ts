import { useEffect, useRef, useCallback, useState } from 'react';
import { useLayoutStore } from '@/lib/stores/layout.store';
import { toast } from '@/hooks/use-toast';

interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  metaKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  callback: (event: KeyboardEvent) => void;
  description?: string;
  enabled?: boolean;
  preventDefault?: boolean;
  stopPropagation?: boolean;
  scope?: 'global' | 'local';
}

interface ShortcutConfig extends KeyboardShortcut {
  id: string;
}

// Platform detection
const isMac = typeof window !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0;

// Shortcut registry
class ShortcutRegistry {
  private shortcuts: Map<string, ShortcutConfig> = new Map();
  private listeners: Map<string, (event: KeyboardEvent) => void> = new Map();

  register(shortcut: KeyboardShortcut): string {
    const id = this.generateId();
    const config: ShortcutConfig = {
      ...shortcut,
      id,
      enabled: shortcut.enabled !== false,
      preventDefault: shortcut.preventDefault !== false,
      stopPropagation: shortcut.stopPropagation !== false,
      scope: shortcut.scope || 'global',
    };

    this.shortcuts.set(id, config);
    return id;
  }

  unregister(id: string): void {
    this.shortcuts.delete(id);
    const listener = this.listeners.get(id);
    if (listener) {
      document.removeEventListener('keydown', listener);
      this.listeners.delete(id);
    }
  }

  enable(id: string): void {
    const shortcut = this.shortcuts.get(id);
    if (shortcut) {
      shortcut.enabled = true;
    }
  }

  disable(id: string): void {
    const shortcut = this.shortcuts.get(id);
    if (shortcut) {
      shortcut.enabled = false;
    }
  }

  handleKeyDown(event: KeyboardEvent): void {
    for (const shortcut of this.shortcuts.values()) {
      if (!shortcut.enabled) continue;

      if (this.matchesShortcut(event, shortcut)) {
        if (shortcut.preventDefault) {
          event.preventDefault();
        }
        if (shortcut.stopPropagation) {
          event.stopPropagation();
        }

        try {
          shortcut.callback(event);
        } catch (error) {
          console.error(`Error in keyboard shortcut handler:`, error);
        }
      }
    }
  }

  private matchesShortcut(event: KeyboardEvent, shortcut: ShortcutConfig): boolean {
    const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase() ||
                     event.code.toLowerCase() === shortcut.key.toLowerCase();

    if (!keyMatch) return false;

    // Check modifier keys
    const ctrlOrMeta = isMac ? event.metaKey : event.ctrlKey;
    const expectedCtrlOrMeta = isMac ? (shortcut.metaKey || shortcut.ctrlKey) : shortcut.ctrlKey;

    if (expectedCtrlOrMeta !== undefined && ctrlOrMeta !== expectedCtrlOrMeta) {
      return false;
    }

    if (shortcut.shiftKey !== undefined && event.shiftKey !== shortcut.shiftKey) {
      return false;
    }

    if (shortcut.altKey !== undefined && event.altKey !== shortcut.altKey) {
      return false;
    }

    // Check if we're in an input field and should ignore the shortcut
    const target = event.target as HTMLElement;
    const isInput = target.tagName === 'INPUT' ||
                   target.tagName === 'TEXTAREA' ||
                   target.contentEditable === 'true';

    // Allow some shortcuts in input fields (e.g., Ctrl+Z for undo)
    const allowedInInput = ['z', 'y', 'a', 'x', 'c', 'v'].includes(shortcut.key.toLowerCase()) &&
                          (shortcut.ctrlKey || shortcut.metaKey);

    if (isInput && !allowedInInput && shortcut.scope === 'global') {
      return false;
    }

    return true;
  }

  private generateId(): string {
    return `shortcut-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  getAll(): ShortcutConfig[] {
    return Array.from(this.shortcuts.values());
  }

  clear(): void {
    this.listeners.forEach(listener => {
      document.removeEventListener('keydown', listener);
    });
    this.shortcuts.clear();
    this.listeners.clear();
  }
}

// Global registry instance
const globalRegistry = new ShortcutRegistry();

export function useKeyboardShortcuts() {
  const [shortcuts, setShortcuts] = useState<ShortcutConfig[]>([]);
  const registeredIds = useRef<Set<string>>(new Set());

  // Layout store integration
  const { undo, redo, resetLayout, clearHistory } = useLayoutStore();

  // Register a shortcut
  const registerShortcut = useCallback((shortcut: KeyboardShortcut): string => {
    const id = globalRegistry.register(shortcut);
    registeredIds.current.add(id);
    setShortcuts(globalRegistry.getAll());
    return id;
  }, []);

  // Unregister a shortcut
  const unregisterShortcut = useCallback((id: string): void => {
    globalRegistry.unregister(id);
    registeredIds.current.delete(id);
    setShortcuts(globalRegistry.getAll());
  }, []);

  // Enable/disable shortcuts
  const enableShortcut = useCallback((id: string): void => {
    globalRegistry.enable(id);
    setShortcuts(globalRegistry.getAll());
  }, []);

  const disableShortcut = useCallback((id: string): void => {
    globalRegistry.disable(id);
    setShortcuts(globalRegistry.getAll());
  }, []);

  // Register default shortcuts
  useEffect(() => {
    const defaultShortcuts: KeyboardShortcut[] = [
      // Undo/Redo
      {
        key: 'z',
        ctrlKey: true,
        callback: () => {
          if (undo()) {
            toast({
              title: 'Undo',
              description: 'Action undone',
              duration: 2000,
            });
          }
        },
        description: 'Undo last action',
      },
      {
        key: 'z',
        ctrlKey: true,
        shiftKey: true,
        callback: () => {
          if (redo()) {
            toast({
              title: 'Redo',
              description: 'Action redone',
              duration: 2000,
            });
          }
        },
        description: 'Redo last action',
      },
      // Alternative redo shortcut
      {
        key: 'y',
        ctrlKey: true,
        callback: () => {
          if (redo()) {
            toast({
              title: 'Redo',
              description: 'Action redone',
              duration: 2000,
            });
          }
        },
        description: 'Redo last action',
      },
      // Reset
      {
        key: 'r',
        ctrlKey: true,
        altKey: true,
        callback: () => {
          resetLayout();
          clearHistory();
          toast({
            title: 'Layout Reset',
            description: 'Dashboard reset to default layout',
            duration: 3000,
          });
        },
        description: 'Reset layout to default',
      },
      // Help
      {
        key: '?',
        shiftKey: true,
        callback: () => {
          showShortcutsHelp();
        },
        description: 'Show keyboard shortcuts',
      },
      // Focus management
      {
        key: 'Tab',
        callback: (e) => {
          // Allow default tab behavior but enhance for drag contexts
          const activeElement = document.activeElement;
          if (activeElement?.getAttribute('role') === 'button' &&
              activeElement?.getAttribute('aria-describedby')?.includes('drag')) {
            // Custom tab behavior in drag contexts
            e.preventDefault();
            focusNextDraggable(e.shiftKey);
          }
        },
        description: 'Navigate between elements',
        preventDefault: false,
      },
      // Escape key
      {
        key: 'Escape',
        callback: () => {
          // Cancel any ongoing operations
          const draggedElement = document.querySelector('[data-dragging="true"]');
          if (draggedElement) {
            draggedElement.removeAttribute('data-dragging');
            toast({
              title: 'Cancelled',
              description: 'Operation cancelled',
              duration: 2000,
            });
          }
        },
        description: 'Cancel current operation',
      },
    ];

    const ids: string[] = [];
    for (const shortcut of defaultShortcuts) {
      const id = registerShortcut(shortcut);
      ids.push(id);
    }

    return () => {
      ids.forEach(id => unregisterShortcut(id));
    };
  }, [undo, redo, resetLayout, clearHistory, registerShortcut, unregisterShortcut]);

  // Global keyboard event handler
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      globalRegistry.handleKeyDown(event);
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      registeredIds.current.forEach(id => {
        globalRegistry.unregister(id);
      });
      registeredIds.current.clear();
    };
  }, []);

  return {
    registerShortcut,
    unregisterShortcut,
    enableShortcut,
    disableShortcut,
    shortcuts,
  };
}

// Helper functions
function focusNextDraggable(reverse: boolean = false): void {
  const draggables = Array.from(
    document.querySelectorAll('[draggable="true"], [data-draggable="true"]')
  ) as HTMLElement[];

  if (draggables.length === 0) return;

  const currentIndex = draggables.findIndex(el => el === document.activeElement);
  let nextIndex: number;

  if (reverse) {
    nextIndex = currentIndex <= 0 ? draggables.length - 1 : currentIndex - 1;
  } else {
    nextIndex = currentIndex >= draggables.length - 1 ? 0 : currentIndex + 1;
  }

  draggables[nextIndex]?.focus();
}

function showShortcutsHelp(): void {
  const shortcuts = globalRegistry.getAll();
  const formattedShortcuts = shortcuts
    .filter(s => s.description)
    .map(s => {
      const keys = [];
      if (s.ctrlKey) keys.push(isMac ? '⌘' : 'Ctrl');
      if (s.shiftKey) keys.push('Shift');
      if (s.altKey) keys.push(isMac ? '⌥' : 'Alt');
      keys.push(s.key.toUpperCase());

      return `${keys.join('+')} - ${s.description}`;
    });

  // You could show this in a modal or toast
  toast({
    title: 'Keyboard Shortcuts',
    description: (
      <div className="space-y-1 mt-2">
        {formattedShortcuts.map((shortcut, index) => (
          <div key={index} className="text-sm font-mono">
            {shortcut}
          </div>
        ))}
      </div>
    ),
    duration: 10000,
  });
}

// Hook for arrow key navigation in drag contexts
export function useArrowKeyNavigation(
  enabled: boolean = true,
  onMove?: (direction: 'up' | 'down' | 'left' | 'right') => void
) {
  const { registerShortcut, unregisterShortcut } = useKeyboardShortcuts();

  useEffect(() => {
    if (!enabled) return;

    const shortcuts = [
      {
        key: 'ArrowUp',
        callback: () => onMove?.('up'),
        description: 'Move up',
      },
      {
        key: 'ArrowDown',
        callback: () => onMove?.('down'),
        description: 'Move down',
      },
      {
        key: 'ArrowLeft',
        callback: () => onMove?.('left'),
        description: 'Move left',
      },
      {
        key: 'ArrowRight',
        callback: () => onMove?.('right'),
        description: 'Move right',
      },
    ];

    const ids = shortcuts.map(s => registerShortcut(s));

    return () => {
      ids.forEach(id => unregisterShortcut(id));
    };
  }, [enabled, onMove, registerShortcut, unregisterShortcut]);
}

// Hook for custom shortcut combinations
export function useCustomShortcut(
  key: string,
  callback: (event: KeyboardEvent) => void,
  options: Partial<KeyboardShortcut> = {}
) {
  const { registerShortcut, unregisterShortcut } = useKeyboardShortcuts();
  const idRef = useRef<string | null>(null);

  useEffect(() => {
    const id = registerShortcut({
      key,
      callback,
      ...options,
    });

    idRef.current = id;

    return () => {
      if (idRef.current) {
        unregisterShortcut(idRef.current);
      }
    };
  }, [key, callback, options, registerShortcut, unregisterShortcut]);

  const enable = useCallback(() => {
    if (idRef.current) {
      globalRegistry.enable(idRef.current);
    }
  }, []);

  const disable = useCallback(() => {
    if (idRef.current) {
      globalRegistry.disable(idRef.current);
    }
  }, []);

  return { enable, disable };
}