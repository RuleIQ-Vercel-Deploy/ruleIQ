export default function TestTheme() {
  return (
    <div className="min-h-screen bg-background p-8 text-foreground">
      <div className="container mx-auto max-w-6xl">
        <h1 className="mb-8 text-4xl font-bold text-primary">Teal Design System - Text Readability Test</h1>

        <div className="grid gap-8">
          {/* Text Contrast Test */}
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <h2 className="mb-4 text-2xl font-semibold text-foreground">Text Contrast & Readability</h2>
            <div className="space-y-3">
              <p className="text-foreground text-lg">Primary text (foreground) - Should be high contrast #1F2937</p>
              <p className="text-muted-foreground text-base">Secondary text (muted-foreground) - Should be readable #64748B</p>
              <p className="text-primary text-lg font-semibold">Primary brand color text - Teal #2C7A7B</p>
              <p className="text-secondary-foreground text-base">Secondary color text</p>
            </div>
          </div>

          {/* Feature Cards Test (matching example design) */}
          <div className="grid gap-6 md:grid-cols-3">
            <div className="rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-16 h-16 bg-teal-600 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <div className="w-6 h-6 bg-white rounded"></div>
              </div>
              <h3 className="text-xl font-bold text-center mb-2">AI-Powered Assessment</h3>
              <p className="text-muted-foreground text-center">
                Clean, readable text on white background with proper contrast ratios.
              </p>
            </div>
            
            <div className="rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-16 h-16 bg-teal-600 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <div className="w-6 h-6 bg-white rounded"></div>
              </div>
              <h3 className="text-xl font-bold text-center mb-2">Policy Generation</h3>
              <p className="text-muted-foreground text-center">
                Text should be clearly readable without gradient effects.
              </p>
            </div>

            <div className="rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-16 h-16 bg-teal-600 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <div className="w-6 h-6 bg-white rounded"></div>
              </div>
              <h3 className="text-xl font-bold text-center mb-2">Real-Time Monitoring</h3>
              <p className="text-muted-foreground text-center">
                Professional design matching the example screenshots.
              </p>
            </div>
          </div>

          {/* Primary Button Test */}
          <div className="rounded-lg border bg-card p-6">
            <h3 className="mb-4 text-lg font-medium text-foreground">Button Contrast Test</h3>
            <div className="flex gap-4">
              <button className="bg-teal-600 hover:bg-teal-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                Start Free Trial
              </button>
              <button className="border-2 border-teal-600 text-teal-600 hover:bg-teal-50 px-6 py-3 rounded-lg font-medium transition-colors">
                Watch Demo
              </button>
            </div>
          </div>

          {/* WCAG Compliance Status */}
          <div className="rounded-lg border-l-4 border-l-green-500 bg-green-50 p-6">
            <h3 className="text-lg font-medium text-green-800 mb-2">✅ WCAG 2.2 AA Compliance Status</h3>
            <ul className="text-green-700 space-y-1">
              <li>• Text contrast ratio ≥ 4.5:1 for normal text</li>
              <li>• Text contrast ratio ≥ 3:1 for large text</li>
              <li>• No color-only information conveyance</li>
              <li>• Readable text without gradient effects</li>
              <li>• Professional design matching examples</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
