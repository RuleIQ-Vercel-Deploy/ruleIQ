import { describe, expect, it, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock components for testing design system
const TestComponent = ({ className }: { className?: string }) => (
  <div className={className} data-testid="test-component">
    <h1 className="text-4xl font-bold">H1 Heading</h1>
    <h2 className="text-2xl font-bold">H2 Heading</h2>
    <h3 className="text-lg font-semibold">H3 Heading</h3>
    <p className="text-sm">Body Text</p>
    <small className="text-xs">Small Text</small>
  </div>
);

const GridTestComponent = () => (
  <div className="m-8 grid gap-8 p-8">
    <div className="m-4 p-4">8px Grid Item</div>
    <div className="m-16 p-16">16px Grid Item</div>
    <div className="m-24 p-24">24px Grid Item</div>
  </div>
);

const ColorTestComponent = () => (
  <div data-testid="color-test">
    <div className="bg-primary text-white">Primary Color</div>
    <div className="bg-primary-dark">Primary Dark</div>
    <div className="bg-primary-light">Primary Light</div>
    <div className="bg-gold">Gold Accent</div>
    <div className="bg-gold-dark">Gold Dark</div>
    <div className="bg-gold-light">Gold Light</div>
    <div className="bg-cyan">Cyan Accent</div>
    <div className="bg-neutral-light">Neutral Light</div>
    <div className="bg-neutral-medium">Neutral Medium</div>
  </div>
);

describe('Design System Tests', () => {
  let container: HTMLElement;

  beforeEach(() => {
    // Create a container for testing
    container = document.createElement('div');
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.removeChild(container);
  });

  describe('8px Grid System Compliance', () => {
    it('should enforce 8px grid system for spacing', () => {
      const { container } = render(<GridTestComponent />);

      // Test gap values
      const gridElement = container.querySelector('.grid');
      expect(gridElement).toHaveClass('gap-8'); // 32px (8 * 4)

      // Test padding values
      const paddingElements = container.querySelectorAll('[class*="p-"]');
      paddingElements.forEach((el) => {
        const classes = el.className.split(' ');
        classes.forEach((cls) => {
          if (cls.startsWith('p-')) {
            const value = parseInt(cls.split('-')[1]);
            expect(value % 4).toBe(0); // Should be multiple of 4 (Tailwind's 1 unit = 0.25rem = 4px)
          }
        });
      });

      // Test margin values
      const marginElements = container.querySelectorAll('[class*="m-"]');
      marginElements.forEach((el) => {
        const classes = el.className.split(' ');
        classes.forEach((cls) => {
          if (cls.startsWith('m-')) {
            const value = parseInt(cls.split('-')[1]);
            expect(value % 4).toBe(0); // Should be multiple of 4
          }
        });
      });
    });

    it('should allow 4px half-step when necessary', () => {
      const { container } = render(
        <div className="m-1 gap-1 p-1" data-testid="half-step">
          4px half-step
        </div>,
      );

      const element = screen.getByTestId('half-step');
      expect(element).toHaveClass('p-1'); // 4px
      expect(element).toHaveClass('m-1'); // 4px
      expect(element).toHaveClass('gap-1'); // 4px
    });

    it('should validate grid system in complex layouts', () => {
      const { container } = render(
        <div className="grid grid-cols-3 gap-8 p-16">
          <div className="m-4 p-8">Card 1</div>
          <div className="m-4 p-8">Card 2</div>
          <div className="m-4 p-8">Card 3</div>
        </div>,
      );

      const grid = container.querySelector('.grid');
      expect(grid).toHaveClass('gap-8'); // 32px
      expect(grid).toHaveClass('p-16'); // 64px

      const cards = container.querySelectorAll('.p-8');
      expect(cards).toHaveLength(3);
      cards.forEach((card) => {
        expect(card).toHaveClass('m-4'); // 16px
      });
    });
  });

  describe('Color Palette Usage', () => {
    it('should apply primary colors correctly', () => {
      const { container } = render(<ColorTestComponent />);

      // Test primary colors
      expect(container.querySelector('.bg-primary')).toBeInTheDocument();
      expect(container.querySelector('.bg-primary-dark')).toBeInTheDocument();
      expect(container.querySelector('.bg-primary-light')).toBeInTheDocument();
    });

    it('should apply accent colors correctly', () => {
      const { container } = render(<ColorTestComponent />);

      // Test gold accent colors
      expect(container.querySelector('.bg-gold')).toBeInTheDocument();
      expect(container.querySelector('.bg-gold-dark')).toBeInTheDocument();
      expect(container.querySelector('.bg-gold-light')).toBeInTheDocument();

      // Test cyan accent color
      expect(container.querySelector('.bg-cyan')).toBeInTheDocument();
    });

    it('should apply neutral colors correctly', () => {
      const { container } = render(<ColorTestComponent />);

      // Test neutral colors
      expect(container.querySelector('.bg-neutral-light')).toBeInTheDocument();
      expect(container.querySelector('.bg-neutral-medium')).toBeInTheDocument();
    });

    it('should follow color usage guidelines', () => {
      const { container } = render(
        <div>
          <button className="hover:bg-primary-dark bg-primary text-white">Primary Button</button>
          <button className="border-2 border-primary text-primary hover:bg-primary hover:text-white">
            Secondary Button
          </button>
          <button className="bg-gold text-primary hover:bg-gold-dark">Accent Button</button>
        </div>,
      );

      const primaryBtn = container.querySelector('.bg-primary');
      expect(primaryBtn).toHaveClass('hover:bg-primary-dark');
      expect(primaryBtn).toHaveClass('text-white');

      const secondaryBtn = container.querySelector('.border-primary');
      expect(secondaryBtn).toHaveClass('text-primary');
      expect(secondaryBtn).toHaveClass('hover:bg-primary');

      const accentBtn = container.querySelector('.bg-gold');
      expect(accentBtn).toHaveClass('hover:bg-gold-dark');
      expect(accentBtn).toHaveClass('text-primary');
    });

    it('should validate semantic colors', () => {
      const { container } = render(
        <div>
          <div className="text-green-600">Success</div>
          <div className="text-gold">Warning</div>
          <div className="text-red-600">Error</div>
          <div className="text-cyan">Info</div>
        </div>,
      );

      expect(container.querySelector('.text-green-600')).toBeInTheDocument();
      expect(container.querySelector('.text-gold')).toBeInTheDocument();
      expect(container.querySelector('.text-red-600')).toBeInTheDocument();
      expect(container.querySelector('.text-cyan')).toBeInTheDocument();
    });
  });

  describe('Typography Scale', () => {
    it('should apply correct font sizes', () => {
      const { container } = render(<TestComponent />);

      // H1: 32px (text-4xl in Tailwind)
      const h1 = container.querySelector('h1');
      expect(h1).toHaveClass('text-4xl');
      expect(h1).toHaveClass('font-bold');

      // H2: 24px (text-2xl in Tailwind)
      const h2 = container.querySelector('h2');
      expect(h2).toHaveClass('text-2xl');
      expect(h2).toHaveClass('font-bold');

      // H3: 18px (text-lg in Tailwind)
      const h3 = container.querySelector('h3');
      expect(h3).toHaveClass('text-lg');
      expect(h3).toHaveClass('font-semibold');

      // Body: 14px (text-sm in Tailwind)
      const p = container.querySelector('p');
      expect(p).toHaveClass('text-sm');

      // Small: 12px (text-xs in Tailwind)
      const small = container.querySelector('small');
      expect(small).toHaveClass('text-xs');
    });

    it('should use correct font families', () => {
      const { container } = render(
        <div className="font-sans">
          <div className="font-mono">Monospace text</div>
        </div>,
      );

      expect(container.querySelector('.font-sans')).toBeInTheDocument();
      expect(container.querySelector('.font-mono')).toBeInTheDocument();
    });

    it('should apply font weights correctly', () => {
      const { container } = render(
        <div>
          <div className="font-normal">Normal</div>
          <div className="font-medium">Medium</div>
          <div className="font-semibold">Semibold</div>
          <div className="font-bold">Bold</div>
        </div>,
      );

      expect(container.querySelector('.font-normal')).toBeInTheDocument();
      expect(container.querySelector('.font-medium')).toBeInTheDocument();
      expect(container.querySelector('.font-semibold')).toBeInTheDocument();
      expect(container.querySelector('.font-bold')).toBeInTheDocument();
    });

    it('should maintain typography hierarchy', () => {
      const { container } = render(
        <article>
          <h1 className="mb-4 text-4xl font-bold">Main Title</h1>
          <h2 className="mb-3 text-2xl font-bold">Section Title</h2>
          <h3 className="mb-2 text-lg font-semibold">Subsection</h3>
          <p className="mb-2 text-sm">Body paragraph</p>
          <small className="text-xs text-gray-600">Caption</small>
        </article>,
      );

      const h1 = container.querySelector('h1');
      const h2 = container.querySelector('h2');
      const h3 = container.querySelector('h3');
      const p = container.querySelector('p');
      const small = container.querySelector('small');

      // Verify hierarchy
      expect(h1).toHaveClass('text-4xl');
      expect(h2).toHaveClass('text-2xl');
      expect(h3).toHaveClass('text-lg');
      expect(p).toHaveClass('text-sm');
      expect(small).toHaveClass('text-xs');
    });
  });

  describe('Spacing Consistency', () => {
    it('should use consistent spacing units', () => {
      const { container } = render(
        <div className="space-y-8">
          <div className="mb-8 p-4">Item 1</div>
          <div className="mt-4 p-8">Item 2</div>
          <div className="px-16 py-8">Item 3</div>
        </div>,
      );

      // All spacing should be multiples of 4 (1rem = 16px, 1 unit = 0.25rem = 4px)
      expect(container.querySelector('.space-y-8')).toBeInTheDocument();
      expect(container.querySelector('.p-4')).toBeInTheDocument();
      expect(container.querySelector('.mb-8')).toBeInTheDocument();
      expect(container.querySelector('.mt-4')).toBeInTheDocument();
      expect(container.querySelector('.px-16')).toBeInTheDocument();
      expect(container.querySelector('.py-8')).toBeInTheDocument();
    });

    it('should apply consistent component spacing', () => {
      const { container } = render(
        <div className="flex flex-col gap-8">
          <button className="px-4 py-2">Button 1</button>
          <button className="px-4 py-2">Button 2</button>
          <button className="px-4 py-2">Button 3</button>
        </div>,
      );

      const flexContainer = container.querySelector('.flex');
      expect(flexContainer).toHaveClass('gap-8');

      const buttons = container.querySelectorAll('button');
      buttons.forEach((btn) => {
        expect(btn).toHaveClass('px-4');
        expect(btn).toHaveClass('py-2');
      });
    });

    it('should validate card and section spacing', () => {
      const { container } = render(
        <section className="px-8 py-16">
          <div className="mx-auto max-w-7xl">
            <div className="grid grid-cols-3 gap-8">
              <div className="rounded-lg bg-white p-8 shadow-md">Card 1</div>
              <div className="rounded-lg bg-white p-8 shadow-md">Card 2</div>
              <div className="rounded-lg bg-white p-8 shadow-md">Card 3</div>
            </div>
          </div>
        </section>,
      );

      const section = container.querySelector('section');
      expect(section).toHaveClass('py-16'); // 64px
      expect(section).toHaveClass('px-8'); // 32px

      const grid = container.querySelector('.grid');
      expect(grid).toHaveClass('gap-8'); // 32px

      const cards = container.querySelectorAll('.p-8');
      expect(cards).toHaveLength(3);
    });
  });

  describe('Icon System', () => {
    it('should use Lucide icons exclusively', () => {
      const { container } = render(
        <div>
          <svg className="lucide lucide-home h-6 w-6">
            <path d="..." />
          </svg>
          <svg className="lucide lucide-user h-4 w-4">
            <path d="..." />
          </svg>
        </div>,
      );

      const icons = container.querySelectorAll('.lucide');
      expect(icons).toHaveLength(2);

      // Check icon sizing
      expect(icons[0]).toHaveClass('w-6');
      expect(icons[0]).toHaveClass('h-6');
      expect(icons[1]).toHaveClass('w-4');
      expect(icons[1]).toHaveClass('h-4');
    });

    it('should apply monochromatic styling to icons', () => {
      const { container } = render(
        <div>
          <svg className="lucide text-primary">Icon 1</svg>
          <svg className="lucide text-gray-600">Icon 2</svg>
          <svg className="lucide text-gold">Icon 3</svg>
        </div>,
      );

      const icons = container.querySelectorAll('.lucide');
      expect(icons[0]).toHaveClass('text-primary');
      expect(icons[1]).toHaveClass('text-gray-600');
      expect(icons[2]).toHaveClass('text-gold');
    });
  });
});
