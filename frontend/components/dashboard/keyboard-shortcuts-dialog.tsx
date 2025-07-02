"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { useKeyboardShortcuts, getShortcutDisplay } from "@/hooks/use-keyboard-shortcuts";

export function KeyboardShortcutsDialog() {
  const [open, setOpen] = useState(false);
  const shortcuts = useKeyboardShortcuts();

  useEffect(() => {
    const handleShowShortcuts = () => setOpen(true);
    document.addEventListener("showKeyboardShortcuts", handleShowShortcuts);
    return () => document.removeEventListener("showKeyboardShortcuts", handleShowShortcuts);
  }, []);

  const globalShortcuts = shortcuts.filter(s => !s.requiresProfile);
  const profileShortcuts = shortcuts.filter(s => s.requiresProfile);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Keyboard Shortcuts</DialogTitle>
          <DialogDescription>
            Quick keyboard shortcuts to navigate and perform actions
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Global Shortcuts */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Global Shortcuts
            </h3>
            <div className="space-y-2">
              {globalShortcuts.map((shortcut, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50"
                >
                  <span className="text-sm text-gray-700">
                    {shortcut.description}
                  </span>
                  <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded">
                    {getShortcutDisplay(shortcut)}
                  </kbd>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Profile-Required Shortcuts */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <h3 className="text-sm font-semibold text-gray-900">
                Quick Actions
              </h3>
              <Badge variant="outline" className="text-xs">
                Requires Profile
              </Badge>
            </div>
            <div className="space-y-2">
              {profileShortcuts.map((shortcut, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50"
                >
                  <span className="text-sm text-gray-700">
                    {shortcut.description}
                  </span>
                  <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded">
                    {getShortcutDisplay(shortcut)}
                  </kbd>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Tips */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-blue-900 mb-2">
              Pro Tips
            </h4>
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