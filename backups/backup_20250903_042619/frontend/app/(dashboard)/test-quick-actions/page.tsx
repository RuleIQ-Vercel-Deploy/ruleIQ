'use client';

export default function TestQuickActionsPage() {
  return (
    <div className="p-8">
      <h1 className="mb-4 text-2xl font-bold">Quick Actions Test Page</h1>
      <p className="mb-4">This page tests the Quick Actions features:</p>

      <div className="space-y-4">
        <div className="rounded border p-4">
          <h2 className="mb-2 font-semibold">1. Floating Action Button</h2>
          <p className="text-sm text-gray-600">
            Look for a gold floating button in the bottom-right corner
          </p>
        </div>

        <div className="rounded border p-4">
          <h2 className="mb-2 font-semibold">2. Command Palette</h2>
          <p className="text-sm text-gray-600">Press ⌘K (Mac) or Ctrl+K (Windows/Linux)</p>
        </div>

        <div className="rounded border p-4">
          <h2 className="mb-2 font-semibold">3. Keyboard Shortcuts</h2>
          <p className="text-sm text-gray-600">Press Shift+? to see all shortcuts</p>
        </div>

        <div className="rounded border p-4">
          <h2 className="mb-2 font-semibold">4. Quick Shortcuts</h2>
          <ul className="space-y-1 text-sm text-gray-600">
            <li>Alt+N - New assessment</li>
            <li>Alt+P - Generate policy</li>
            <li>Alt+U - Upload evidence</li>
            <li>Alt+I - Open IQ chat</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
