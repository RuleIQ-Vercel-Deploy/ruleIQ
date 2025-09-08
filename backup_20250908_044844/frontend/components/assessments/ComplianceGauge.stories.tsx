import { ComplianceGauge } from './ComplianceGauge';

import type { Meta, StoryObj } from '@storybook/react';

const meta = {
  title: 'Assessments/ComplianceGauge',
  component: ComplianceGauge,
  parameters: {
    layout: 'centered',
    chromatic: {
      viewports: [375, 768, 1440],
      delay: 500, // Allow animation to complete
    },
  },
  tags: ['autodocs'],
  argTypes: {
    score: {
      control: { type: 'range', min: 0, max: 100, step: 1 },
    },
    size: {
      control: { type: 'range', min: 100, max: 400, step: 50 },
    },
  },
} satisfies Meta<typeof ComplianceGauge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    score: 75,
  },
};

export const HighCompliance: Story = {
  args: {
    score: 92,
  },
};

export const MediumCompliance: Story = {
  args: {
    score: 65,
  },
};

export const LowCompliance: Story = {
  args: {
    score: 35,
  },
};

export const CriticalCompliance: Story = {
  args: {
    score: 15,
  },
};

export const PerfectScore: Story = {
  args: {
    score: 100,
  },
};

export const ZeroScore: Story = {
  args: {
    score: 0,
  },
};

export const SmallSize: Story = {
  args: {
    score: 75,
    size: 150,
  },
};

export const LargeSize: Story = {
  args: {
    score: 75,
    size: 300,
  },
};

export const WithoutLabel: Story = {
  args: {
    score: 75,
  },
};

export const WithoutAnimation: Story = {
  args: {
    score: 75,
  },
};

export const AllScoreLevels: Story = {
  args: {
    score: 75,
  },
  render: () => (
    <div className="grid grid-cols-2 gap-8 sm:grid-cols-3 md:grid-cols-5">
      <div className="text-center">
        <ComplianceGauge score={0} />
        <p className="mt-2 text-sm font-medium">Critical (0%)</p>
      </div>
      <div className="text-center">
        <ComplianceGauge score={25} />
        <p className="mt-2 text-sm font-medium">Low (25%)</p>
      </div>
      <div className="text-center">
        <ComplianceGauge score={50} />
        <p className="mt-2 text-sm font-medium">Medium (50%)</p>
      </div>
      <div className="text-center">
        <ComplianceGauge score={75} />
        <p className="mt-2 text-sm font-medium">Good (75%)</p>
      </div>
      <div className="text-center">
        <ComplianceGauge score={100} />
        <p className="mt-2 text-sm font-medium">Excellent (100%)</p>
      </div>
    </div>
  ),
  parameters: {
    layout: 'padded',
  },
};

export const AllSizes: Story = {
  args: {
    score: 75,
  },
  render: () => (
    <div className="flex items-center justify-center gap-8">
      <div className="text-center">
        <ComplianceGauge score={75} size={150} />
        <p className="mt-2 text-sm">Small</p>
      </div>
      <div className="text-center">
        <ComplianceGauge score={75} size={200} />
        <p className="mt-2 text-sm">Medium</p>
      </div>
      <div className="text-center">
        <ComplianceGauge score={75} size={300} />
        <p className="mt-2 text-sm">Large</p>
      </div>
    </div>
  ),
};

export const ResponsiveGrid: Story = {
  args: {
    score: 75,
  },
  render: () => (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div className="rounded-lg border p-4">
        <h3 className="mb-4 text-sm font-medium">GDPR Compliance</h3>
        <ComplianceGauge score={85} />
      </div>
      <div className="rounded-lg border p-4">
        <h3 className="mb-4 text-sm font-medium">ISO 27001</h3>
        <ComplianceGauge score={72} />
      </div>
      <div className="rounded-lg border p-4">
        <h3 className="mb-4 text-sm font-medium">HIPAA</h3>
        <ComplianceGauge score={45} />
      </div>
      <div className="rounded-lg border p-4">
        <h3 className="mb-4 text-sm font-medium">SOC 2</h3>
        <ComplianceGauge score={93} />
      </div>
    </div>
  ),
  parameters: {
    layout: 'padded',
    chromatic: {
      viewports: [375, 768, 1440],
    },
  },
};

export const DarkMode: Story = {
  args: {
    score: 75,
  },
  parameters: {
    backgrounds: { default: 'dark' },
  },
  decorators: [
    (Story) => (
      <div className="dark">
        <Story />
      </div>
    ),
  ],
};
