export default function TestTheme() {
  return (
    <div className="min-h-screen bg-background p-8 text-foreground">
      <div className="container mx-auto max-w-4xl">
        <h1 className="mb-8 text-4xl font-bold text-primary">Theme Migration Test</h1>

        <div className="grid gap-6">
          <div className="rounded-lg border bg-card p-6">
            <h2 className="mb-4 text-2xl font-semibold text-foreground">Color Tokens Test</h2>
            <div className="space-y-2">
              <p className="text-foreground">Primary text (foreground)</p>
              <p className="text-muted-foreground">Secondary text (muted-foreground)</p>
              <p className="text-primary">Primary brand color</p>
              <p className="text-secondary">Secondary color</p>
            </div>
          </div>

          <div className="rounded-lg border border-primary bg-primary/10 p-6">
            <h3 className="mb-2 text-lg font-medium text-primary">Primary Background</h3>
            <p className="text-primary-foreground">This should show the new teal theme colors</p>
          </div>

          <div className="rounded-lg bg-muted p-6">
            <h3 className="mb-2 text-lg font-medium text-muted-foreground">Muted Background</h3>
            <p className="text-foreground">Testing muted background colors</p>
          </div>
        </div>
      </div>
    </div>
  );
}
