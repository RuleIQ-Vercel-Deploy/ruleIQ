'use client';

import { useEffect, useState } from 'react';

import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Separator } from '@/components/ui/separator';
// Static shortcuts data for display
const staticShortcuts = [
  { key: 'Z', ctrlKey: true, description: 'Undo last action' },
  { key: 'Z', ctrlKey: true, shiftKey: true, description: 'Redo last action' },
  { key: 'Y', ctrlKey: true, description: 'Redo last action' },
  { key: 'R', ctrlKey: true, altKey: true, description: 'Reset layout to default' },
  { key: '?', shiftKey: true, description: 'Show keyboard shortcuts' },
  { key: 'Escape', description: 'Cancel current operation' },
];

// Helper function to display shortcuts
const getShortcutDisplay = (shortcut: any): string => {
  const parts = [];
  
  if (shortcut.ctrlKey || shortcut.metaKey) {
    parts.push(typeof window !== 'undefined' && navigator.platform.includes('Mac') ? '⌘' : 'Ctrl');
  }
  if (shortcut.altKey) {
    parts.push(typeof window !== 'undefined' && navigator.platform.includes('Mac') ? '⌥' : 'Alt');
  }
  if (shortcut.shiftKey) {
    parts.push('⇧');
  }
  
  parts.push(shortcut.key.toUpperCase());
  
  return parts.join(' + ');
};

export function KeyboardShortcutsDialog() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handleShowShortcuts = () => setOpen(true);
    document.addEventListener('showKeyboardShortcuts', handleShowShortcuts);
    return () => document.removeEventListener('showKeyboardShortcuts', handleShowShortcuts);
  }, []);

  // Use static shortcuts for now
  const globalShortcuts = staticShortcuts;
  const profileShortcuts: typeof staticShortcuts = []; // Empty for now

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="max-h-[80vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Keyboard Shortcuts</DialogTitle>
          <DialogDescription>
            Quick keyboard shortcuts to navigate and perform actions
          </DialogDescription>
        </DialogHeader>

        <div className="mt-4 space-y-6">
          {/* Global Shortcuts */}
          <div>
            <h3 className="mb-3 text-sm font-semibold text-gray-900">Global Shortcuts</h3>
            <div className="space-y-2">
              {globalShortcuts.map((shortcut, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-gray-50"
                >
                  <span className="text-sm text-gray-700">{shortcut.description}</span>
                  <kbd className="rounded border border-gray-200 bg-gray-100 px-2 py-1 text-xs font-semibold text-gray-800">
                    {getShortcutDisplay(shortcut)}
                  </kbd>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Profile-Required Shortcuts */}
          <div>
            <div className="mb-3 flex items-center gap-2">
              <h3 className="text-sm font-semibold text-gray-900">Quick Actions</h3>
              <Badge variant="outline" className="text-xs">
                Requires Profile
              </Badge>
            </div>
            <div className="space-y-2">
              {profileShortcuts.map((shortcut, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-gray-50"
                >
                  <span className="text-sm text-gray-700">{shortcut.description}</span>
                  <kbd className="rounded border border-gray-200 bg-gray-100 px-2 py-1 text-xs font-semibold text-gray-800">
                    {getShortcutDisplay(shortcut)}
                  </kbd>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Tips */}
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
            <h4 className="mb-2 text-sm font-semibold text-blue-900">Pro Tips</h4>
            <ul className="space-y-1 text-sm text-blue-800">
              <li>• Use ⌘K to quickly search and navigate anywhere</li>
              <li>• Alt + shortcuts work from any page in the dashboard</li>
              <li>• Press ? to show this help dialog anytime</li>
            </ul>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
