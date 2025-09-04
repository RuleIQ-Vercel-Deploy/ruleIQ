import { Mail, Loader2, ChevronRight } from 'lucide-react';

import { Button } from './button';

import type { Meta, StoryObj } from '@storybook/react';

const meta = {
  title: 'UI/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    chromatic: { viewports: [375, 768, 1440] },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
    },
    size: {
      control: 'select',
      options: ['default', 'sm', 'lg', 'icon'],
    },
    asChild: {
      control: 'boolean',
    },
    disabled: {
      control: 'boolean',
    },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

// Basic variants
export const Default: Story = {
  args: {
    children: 'Button',
  },
};

export const Primary: Story = {
  args: {
    variant: 'default',
    children: 'Primary Button',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Secondary Button',
  },
};

export const Destructive: Story = {
  args: {
    variant: 'destructive',
    children: 'Delete',
  },
};

export const Outline: Story = {
  args: {
    variant: 'outline',
    children: 'Outline Button',
  },
};

export const Ghost: Story = {
  args: {
    variant: 'ghost',
    children: 'Ghost Button',
  },
};

export const Link: Story = {
  args: {
    variant: 'link',
    children: 'Link Button',
  },
};

// Sizes
export const Small: Story = {
  args: {
    size: 'sm',
    children: 'Small Button',
  },
};

export const Large: Story = {
  args: {
    size: 'lg',
    children: 'Large Button',
  },
};

export const Icon: Story = {
  args: {
    size: 'icon',
    children: <Mail className="h-4 w-4" />,
  },
};

// States
export const Disabled: Story = {
  args: {
    disabled: true,
    children: 'Disabled Button',
  },
};

export const Loading: Story = {
  args: {
    disabled: true,
    children: (
      <>
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        Loading...
      </>
    ),
  },
};

// With Icons
export const WithLeftIcon: Story = {
  args: {
    children: (
      <>
        <Mail className="mr-2 h-4 w-4" />
        Email
      </>
    ),
  },
};

export const WithRightIcon: Story = {
  args: {
    children: (
      <>
        Continue
        <ChevronRight className="ml-2 h-4 w-4" />
      </>
    ),
  },
};

// All Variants Display
export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex gap-2">
        <Button variant="default">Default</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="destructive">Destructive</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="link">Link</Button>
      </div>
      <div className="flex gap-2">
        <Button variant="default" disabled>
          Default Disabled
        </Button>
        <Button variant="secondary" disabled>
          Secondary Disabled
        </Button>
        <Button variant="destructive" disabled>
          Destructive Disabled
        </Button>
        <Button variant="outline" disabled>
          Outline Disabled
        </Button>
        <Button variant="ghost" disabled>
          Ghost Disabled
        </Button>
        <Button variant="link" disabled>
          Link Disabled
        </Button>
      </div>
    </div>
  ),
};

// All Sizes Display
export const AllSizes: Story = {
  render: () => (
    <div className="flex items-center gap-2">
      <Button size="sm">Small</Button>
      <Button size="default">Default</Button>
      <Button size="lg">Large</Button>
      <Button size="icon">
        <Mail className="h-4 w-4" />
      </Button>
    </div>
  ),
};

// Interactive States
export const InteractiveStates: Story = {
  render: () => (
    <div className="grid grid-cols-3 gap-4">
      <div>
        <p className="mb-2 text-sm font-medium">Normal</p>
        <Button>Button</Button>
      </div>
      <div>
        <p className="mb-2 text-sm font-medium">Hover</p>
        <Button className="hover:bg-primary/90">Button</Button>
      </div>
      <div>
        <p className="mb-2 text-sm font-medium">Focus</p>
        <Button className="focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
          Button
        </Button>
      </div>
    </div>
  ),
};

// Responsive Button
export const ResponsiveButton: Story = {
  render: () => <Button className="w-full sm:w-auto">Responsive Button</Button>,
  parameters: {
    chromatic: {
      viewports: [375, 768, 1440],
    },
  },
};
