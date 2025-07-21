'use client';

import { Button } from '@/components/ui/button';
import {
  Typography,
  H1,
  H2,
  H3,
  Body,
  Small,
  DisplayLarge,
  DisplayMedium,
  Caption,
  Overline,
} from '@/components/ui/typography';

export default function DesignSystemPage() {
  return (
    <div className="container mx-auto space-y-12 p-8">
      {/* Typography Section */}
      <section className="space-y-8">
        <H1 className="border-neutral-light border-b pb-4">Typography System</H1>

        <div className="space-y-4">
          <DisplayLarge>Display Large (60px)</DisplayLarge>
          <DisplayMedium>Display Medium (48px)</DisplayMedium>
          <H1>Heading 1 (32px Bold)</H1>
          <H2>Heading 2 (24px Bold)</H2>
          <H3>Heading 3 (18px Semi-Bold)</H3>
          <Body>
            Body Text (14px Regular) - This is the standard body text used throughout the
            application.
          </Body>
          <Typography variant="body-lg">
            Body Large (16px) - For emphasized body content.
          </Typography>
          <Typography variant="body-emphasis">
            Body Emphasis (14px Medium) - For important body text.
          </Typography>
          <Small>Small Text (12px) - For secondary information and captions.</Small>
          <Caption>Caption Text - For image captions and supplementary info.</Caption>
          <Overline>Overline Text - For section labels</Overline>
        </div>

        {/* Typography with Colors */}
        <div className="space-y-4">
          <H3 className="mt-8">Typography Colors</H3>
          <Typography color="primary">Primary Text - Primary brand color</Typography>
          <Typography color="accent">Accent Text - Accent color for highlights</Typography>
          <Typography color="brand">Brand Text - Brand color</Typography>
          <Typography color="muted">Muted Text - Secondary information</Typography>
          <Typography color="error">Error Text - For error messages</Typography>
          <Typography color="success">Success Text - For success messages</Typography>
          <Typography color="warning">Warning Text - For warnings</Typography>
        </div>
      </section>

      {/* Button Section */}
      <section className="space-y-8">
        <H1 className="border-neutral-light border-b pb-4">Button System</H1>

        {/* Primary Actions */}
        <div className="space-y-4">
          <H3>Primary Actions</H3>
          <div className="flex flex-wrap gap-4">
            <Button variant="default">Default Button</Button>
            <Button variant="default">Navy Button</Button>
            <Button variant="secondary">Gold Accent</Button>
            <Button variant="outline">Outline Navy</Button>
          </div>
        </div>

        {/* Semantic Buttons */}
        <div className="space-y-4">
          <H3>Semantic Actions</H3>
          <div className="flex flex-wrap gap-4">
            <Button variant="secondary">Success</Button>
            <Button variant="outline">Warning</Button>
            <Button variant="destructive">Error</Button>
            <Button variant="destructive">Destructive</Button>
          </div>
        </div>

        {/* Button Sizes */}
        <div className="space-y-4">
          <H3>Button Sizes</H3>
          <div className="flex flex-wrap items-center gap-4">
            <Button size="sm">Small</Button>
            <Button size="default">Default</Button>
            <Button size="lg">Large</Button>
          </div>
        </div>

        {/* Button States */}
        <div className="space-y-4">
          <H3>Button States</H3>
          <div className="flex flex-wrap gap-4">
            <Button>Normal</Button>
            <Button disabled>Disabled</Button>
            <Button loading>Loading</Button>
          </div>
        </div>
      </section>

      {/* Color Palette */}
      <section className="space-y-8">
        <H1 className="border-neutral-light border-b pb-4">Color Palette</H1>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Navy Colors */}
          <div className="space-y-2">
            <H3>Navy (Primary)</H3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <div className="h-12 w-20 rounded bg-navy shadow-sm"></div>
                <Caption>#17255A</Caption>
              </div>
              <div className="flex items-center gap-3">
                <div className="bg-navy-dark h-12 w-20 rounded shadow-sm"></div>
                <Caption>#0F1938 (Dark)</Caption>
              </div>
              <div className="flex items-center gap-3">
                <div className="bg-navy-light h-12 w-20 rounded shadow-sm"></div>
                <Caption>#2B3A6A (Light)</Caption>
              </div>
            </div>
          </div>

          {/* Gold Colors */}
          <div className="space-y-2">
            <H3>Gold (Accent)</H3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <div className="h-12 w-20 rounded bg-gold shadow-sm"></div>
                <Caption>#CB963E</Caption>
              </div>
              <div className="flex items-center gap-3">
                <div className="h-12 w-20 rounded bg-gold-dark shadow-sm"></div>
                <Caption>#A67A2E (Dark)</Caption>
              </div>
              <div className="flex items-center gap-3">
                <div className="bg-gold-light h-12 w-20 rounded shadow-sm"></div>
                <Caption>#E0B567 (Light)</Caption>
              </div>
            </div>
          </div>

          {/* Cyan Colors */}
          <div className="space-y-2">
            <H3>Cyan (Energy)</H3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <div className="bg-cyan h-12 w-20 rounded shadow-sm"></div>
                <Caption>#34FEF7</Caption>
              </div>
              <div className="flex items-center gap-3">
                <div className="bg-cyan-dark h-12 w-20 rounded shadow-sm"></div>
                <Caption>#1FD4E5 (Dark)</Caption>
              </div>
              <div className="flex items-center gap-3">
                <div className="bg-cyan-light h-12 w-20 rounded shadow-sm"></div>
                <Caption>#6FFEFB (Light)</Caption>
              </div>
            </div>
          </div>

          {/* Neutral Colors */}
          <div className="space-y-2">
            <H3>Neutral</H3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <div className="bg-neutral-light h-12 w-20 rounded shadow-sm"></div>
                <Caption>#D0D5E3 (Light)</Caption>
              </div>
              <div className="flex items-center gap-3">
                <div className="bg-neutral-medium h-12 w-20 rounded shadow-sm"></div>
                <Caption>#C2C2C2 (Medium)</Caption>
              </div>
              <div className="flex items-center gap-3">
                <div className="bg-neutral-dark h-12 w-20 rounded shadow-sm"></div>
                <Caption>#6B7280 (Dark)</Caption>
              </div>
            </div>
          </div>

          {/* Semantic Colors */}
          <div className="space-y-2">
            <H3>Semantic</H3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <div className="h-12 w-20 rounded bg-success shadow-sm"></div>
                <Caption>#28A745 (Success)</Caption>
              </div>
              <div className="flex items-center gap-3">
                <div className="h-12 w-20 rounded bg-warning shadow-sm"></div>
                <Caption>#CB963E (Warning)</Caption>
              </div>
              <div className="flex items-center gap-3">
                <div className="h-12 w-20 rounded bg-error shadow-sm"></div>
                <Caption>#DC3545 (Error)</Caption>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Spacing Grid */}
      <section className="space-y-8">
        <H1 className="border-neutral-light border-b pb-4">8px Grid System</H1>

        <div className="space-y-4">
          <Typography>
            All spacing follows an 8px grid system. Use these values for margins, padding, and gaps:
          </Typography>

          <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
            {[
              { size: '0.5', px: '4px' },
              { size: '1', px: '8px' },
              { size: '2', px: '16px' },
              { size: '3', px: '24px' },
              { size: '4', px: '32px' },
              { size: '5', px: '40px' },
              { size: '6', px: '48px' },
              { size: '8', px: '64px' },
              { size: '10', px: '80px' },
              { size: '12', px: '96px' },
              { size: '16', px: '128px' },
              { size: '20', px: '160px' },
            ].map(({ size, px }) => (
              <div key={size} className="text-center">
                <div className={`bg-navy h-${size} mb-2 w-full rounded`}></div>
                <Caption>p-{size}</Caption>
                <Caption className="text-muted-foreground">({px})</Caption>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
