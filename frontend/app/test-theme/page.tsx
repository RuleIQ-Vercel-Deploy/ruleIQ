export default function TestTheme() {
  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="container mx-auto max-w-4xl">
        <h1 className="text-4xl font-bold text-primary mb-8">Theme Migration Test</h1>
        
        <div className="grid gap-6">
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-2xl font-semibold text-foreground mb-4">Color Tokens Test</h2>
            <div className="space-y-2">
              <p className="text-foreground">Primary text (foreground)</p>
              <p className="text-muted-foreground">Secondary text (muted-foreground)</p>
              <p className="text-primary">Primary brand color</p>
              <p className="text-secondary">Secondary color</p>
            </div>
          </div>
          
          <div className="bg-primary/10 p-6 rounded-lg border border-primary">
            <h3 className="text-lg font-medium text-primary mb-2">Primary Background</h3>
            <p className="text-primary-foreground">This should show the new teal theme colors</p>
          </div>
          
          <div className="bg-muted p-6 rounded-lg">
            <h3 className="text-lg font-medium text-muted-foreground mb-2">Muted Background</h3>
            <p className="text-foreground">Testing muted background colors</p>
          </div>
        </div>
      </div>
    </div>
  );
}