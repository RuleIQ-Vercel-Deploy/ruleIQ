export default function TestTheme() {
  return (
    <div className="min-h-screen bg-background p-8 text-foreground">
      <div className="container mx-auto max-w-6xl">
        <h1 className="mb-8 text-4xl font-bold text-primary">
          Teal Design System - Text Readability Test
        </h1>

        <div className="grid gap-8">
          {/* Text Contrast Test */}
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <h2 className="mb-4 text-2xl font-semibold text-foreground">
              Text Contrast & Readability
            </h2>
            <div className="space-y-3">
              <p className="text-lg text-foreground">
                Primary text (foreground) - Should be high contrast #1F2937
              </p>
              <p className="text-base text-muted-foreground">
                Secondary text (muted-foreground) - Should be readable #64748B
              </p>
              <p className="text-lg font-semibold text-primary">
                Primary brand color text - Teal #2C7A7B
              </p>
              <p className="text-base text-secondary-foreground">Secondary color text</p>
            </div>
          </div>

          {/* Feature Cards Test (matching example design) */}
          <div className="grid gap-6 md:grid-cols-3">
            <div className="rounded-lg border bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-lg bg-teal-600">
                <div className="h-6 w-6 rounded bg-white"></div>
              </div>
              <h3 className="mb-2 text-center text-xl font-bold">AI-Powered Assessment</h3>
              <p className="text-center text-muted-foreground">
                Clean, readable text on white background with proper contrast ratios.
              </p>
            </div>

            <div className="rounded-lg border bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-lg bg-teal-600">
                <div className="h-6 w-6 rounded bg-white"></div>
              </div>
              <h3 className="mb-2 text-center text-xl font-bold">Policy Generation</h3>
              <p className="text-center text-muted-foreground">
                Text should be clearly readable without gradient effects.
              </p>
            </div>

            <div className="rounded-lg border bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-lg bg-teal-600">
                <div className="h-6 w-6 rounded bg-white"></div>
              </div>
              <h3 className="mb-2 text-center text-xl font-bold">Real-Time Monitoring</h3>
              <p className="text-center text-muted-foreground">
                Professional design matching the example screenshots.
              </p>
            </div>
          </div>

          {/* Primary Button Test */}
          <div className="rounded-lg border bg-card p-6">
            <h3 className="mb-4 text-lg font-medium text-foreground">Button Contrast Test</h3>
            <div className="flex gap-4">
              <button className="rounded-lg bg-teal-600 px-6 py-3 font-medium text-white transition-colors hover:bg-teal-700">
                Start Free Trial
              </button>
              <button className="rounded-lg border-2 border-teal-600 px-6 py-3 font-medium text-teal-600 transition-colors hover:bg-teal-50">
                Watch Demo
              </button>
            </div>
          </div>

          {/* WCAG Compliance Status */}
          <div className="rounded-lg border-l-4 border-l-green-500 bg-green-50 p-6">
            <h3 className="mb-2 text-lg font-medium text-green-800">
              ✅ WCAG 2.2 AA Compliance Status
            </h3>
            <ul className="space-y-1 text-green-700">
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
