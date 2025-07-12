import { describe, expect, it, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock window.matchMedia for responsive tests
const createMatchMedia = (width: number) => {
  return (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => true,
  });
};

// Test components for responsive behavior
const ResponsiveComponent = () => (
  <div className="container mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16">
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      <div className="col-span-1">Item 1</div>
      <div className="col-span-1">Item 2</div>
      <div className="col-span-1">Item 3</div>
      <div className="col-span-1">Item 4</div>
      <div className="col-span-1">Item 5</div>
    </div>
  </div>
);

const MobileFirstComponent = () => (
  <div className="text-sm md:text-base lg:text-lg">
    <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl">Responsive Heading</h1>
    <p className="mt-2 sm:mt-4 md:mt-6 lg:mt-8">Responsive spacing</p>
    <button className="px-3 py-1 sm:px-4 sm:py-2 md:px-6 md:py-3">
      Responsive Button
    </button>
  </div>
);

const BreakpointComponent = () => (
  <div>
    <div className="block sm:hidden">Mobile Only</div>
    <div className="hidden sm:block md:hidden">Small Screen Only</div>
    <div className="hidden md:block lg:hidden">Medium Screen Only</div>
    <div className="hidden lg:block xl:hidden">Large Screen Only</div>
    <div className="hidden xl:block">Extra Large Screen Only</div>
  </div>
);

const NavigationComponent = () => (
  <nav className="bg-primary">
    <div className="container mx-auto">
      {/* Mobile Navigation */}
      <div className="flex md:hidden justify-between items-center p-4">
        <div className="text-white font-bold">Logo</div>
        <button className="text-white">
          <svg className="w-6 h-6" fill="none" stroke="currentColor">
            <path d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
      
      {/* Desktop Navigation */}
      <div className="hidden md:flex justify-between items-center p-4">
        <div className="text-white font-bold">Logo</div>
        <div className="flex gap-6">
          <a href="#" className="text-white hover:text-gold">Home</a>
          <a href="#" className="text-white hover:text-gold">About</a>
          <a href="#" className="text-white hover:text-gold">Services</a>
          <a href="#" className="text-white hover:text-gold">Contact</a>
        </div>
      </div>
    </div>
  </nav>
);

const CardLayoutComponent = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
    <div className="bg-white p-4 md:p-6 lg:p-8 rounded-lg shadow-md">
      <h3 className="text-lg md:text-xl font-semibold">Card 1</h3>
      <p className="mt-2 text-sm md:text-base">Card content</p>
    </div>
    <div className="bg-white p-4 md:p-6 lg:p-8 rounded-lg shadow-md">
      <h3 className="text-lg md:text-xl font-semibold">Card 2</h3>
      <p className="mt-2 text-sm md:text-base">Card content</p>
    </div>
    <div className="bg-white p-4 md:p-6 lg:p-8 rounded-lg shadow-md md:col-span-2 lg:col-span-1">
      <h3 className="text-lg md:text-xl font-semibold">Card 3</h3>
      <p className="mt-2 text-sm md:text-base">Card content</p>
    </div>
  </div>
);

describe('Responsive Design Tests', () => {
  let originalMatchMedia: typeof window.matchMedia;

  beforeEach(() => {
    originalMatchMedia = window.matchMedia;
  });

  afterEach(() => {
    window.matchMedia = originalMatchMedia;
  });

  describe('Mobile-First Approach', () => {
    it('should start with mobile styles and enhance for larger screens', () => {
      const { container } = render(<MobileFirstComponent />);
      
      // Base mobile styles
      const div = container.querySelector('div');
      expect(div).toHaveClass('text-sm');
      
      // Progressive enhancement
      expect(div).toHaveClass('md:text-base');
      expect(div).toHaveClass('lg:text-lg');
      
      const heading = container.querySelector('h1');
      expect(heading).toHaveClass('text-2xl'); // Mobile
      expect(heading).toHaveClass('sm:text-3xl');
      expect(heading).toHaveClass('md:text-4xl');
      expect(heading).toHaveClass('lg:text-5xl');
    });

    it('should apply mobile-first spacing', () => {
      const { container } = render(<MobileFirstComponent />);
      
      const paragraph = container.querySelector('p');
      expect(paragraph).toHaveClass('mt-2'); // Mobile
      expect(paragraph).toHaveClass('sm:mt-4');
      expect(paragraph).toHaveClass('md:mt-6');
      expect(paragraph).toHaveClass('lg:mt-8');
    });

    it('should use mobile-first button sizing', () => {
      const { container } = render(<MobileFirstComponent />);
      
      const button = container.querySelector('button');
      expect(button).toHaveClass('px-3', 'py-1'); // Mobile
      expect(button).toHaveClass('sm:px-4', 'sm:py-2');
      expect(button).toHaveClass('md:px-6', 'md:py-3');
    });
  });

  describe('Breakpoint Behavior', () => {
    it('should handle sm breakpoint (640px)', () => {
      window.matchMedia = createMatchMedia(640);
      const { container } = render(<BreakpointComponent />);
      
      // Check visibility classes
      expect(container.querySelector('.block.sm\\:hidden')).toBeInTheDocument();
      expect(container.querySelector('.hidden.sm\\:block')).toBeInTheDocument();
    });

    it('should handle md breakpoint (768px)', () => {
      window.matchMedia = createMatchMedia(768);
      const { container } = render(<BreakpointComponent />);
      
      expect(container.querySelector('.hidden.md\\:block')).toBeInTheDocument();
      expect(container.querySelector('.md\\:hidden')).toBeInTheDocument();
    });

    it('should handle lg breakpoint (1024px)', () => {
      window.matchMedia = createMatchMedia(1024);
      const { container } = render(<BreakpointComponent />);
      
      expect(container.querySelector('.hidden.lg\\:block')).toBeInTheDocument();
      expect(container.querySelector('.lg\\:hidden')).toBeInTheDocument();
    });

    it('should handle xl breakpoint (1280px)', () => {
      window.matchMedia = createMatchMedia(1280);
      const { container } = render(<BreakpointComponent />);
      
      expect(container.querySelector('.hidden.xl\\:block')).toBeInTheDocument();
      expect(container.querySelector('.xl\\:hidden')).toBeInTheDocument();
    });

    it('should validate breakpoint order consistency', () => {
      const { container } = render(
        <div className="w-full sm:w-3/4 md:w-2/3 lg:w-1/2 xl:w-1/3">
          Progressive Width
        </div>
      );
      
      const div = container.querySelector('div');
      expect(div).toHaveClass('w-full'); // Mobile: 100%
      expect(div).toHaveClass('sm:w-3/4'); // Small: 75%
      expect(div).toHaveClass('md:w-2/3'); // Medium: 66.67%
      expect(div).toHaveClass('lg:w-1/2'); // Large: 50%
      expect(div).toHaveClass('xl:w-1/3'); // Extra Large: 33.33%
    });
  });

  describe('Responsive Component Layouts', () => {
    it('should handle responsive grid layouts', () => {
      const { container } = render(<ResponsiveComponent />);
      
      const grid = container.querySelector('.grid');
      expect(grid).toHaveClass('grid-cols-1'); // Mobile: 1 column
      expect(grid).toHaveClass('sm:grid-cols-2'); // Small: 2 columns
      expect(grid).toHaveClass('md:grid-cols-3'); // Medium: 3 columns
      expect(grid).toHaveClass('lg:grid-cols-4'); // Large: 4 columns
      expect(grid).toHaveClass('xl:grid-cols-5'); // Extra Large: 5 columns
    });

    it('should handle responsive container padding', () => {
      const { container } = render(<ResponsiveComponent />);
      
      const containerDiv = container.querySelector('.container');
      expect(containerDiv).toHaveClass('px-4'); // Mobile
      expect(containerDiv).toHaveClass('sm:px-6');
      expect(containerDiv).toHaveClass('md:px-8');
      expect(containerDiv).toHaveClass('lg:px-12');
      expect(containerDiv).toHaveClass('xl:px-16');
    });

    it('should handle responsive navigation', () => {
      const { container } = render(<NavigationComponent />);
      
      // Mobile navigation
      const mobileNav = container.querySelector('.flex.md\\:hidden');
      expect(mobileNav).toBeInTheDocument();
      
      // Desktop navigation
      const desktopNav = container.querySelector('.hidden.md\\:flex');
      expect(desktopNav).toBeInTheDocument();
    });

    it('should handle responsive card layouts', () => {
      const { container } = render(<CardLayoutComponent />);
      
      const grid = container.querySelector('.grid');
      expect(grid).toHaveClass('grid-cols-1'); // Mobile: 1 column
      expect(grid).toHaveClass('md:grid-cols-2'); // Medium: 2 columns
      expect(grid).toHaveClass('lg:grid-cols-3'); // Large: 3 columns
      
      // Check responsive padding on cards
      const cards = container.querySelectorAll('.bg-white');
      cards.forEach(card => {
        expect(card).toHaveClass('p-4'); // Mobile
        expect(card).toHaveClass('md:p-6');
        expect(card).toHaveClass('lg:p-8');
      });
      
      // Check responsive column spanning
      const spanningCard = container.querySelector('.md\\:col-span-2');
      expect(spanningCard).toBeInTheDocument();
      expect(spanningCard).toHaveClass('lg:col-span-1');
    });
  });

  describe('Viewport-Specific Styling', () => {
    it('should handle responsive text alignment', () => {
      const { container } = render(
        <div className="text-center sm:text-left md:text-right lg:text-center">
          Responsive Text Alignment
        </div>
      );
      
      const div = container.querySelector('div');
      expect(div).toHaveClass('text-center'); // Mobile
      expect(div).toHaveClass('sm:text-left');
      expect(div).toHaveClass('md:text-right');
      expect(div).toHaveClass('lg:text-center');
    });

    it('should handle responsive flexbox layouts', () => {
      const { container } = render(
        <div className="flex flex-col sm:flex-row md:flex-col lg:flex-row">
          <div className="w-full sm:w-1/2 md:w-full lg:w-1/3">Item 1</div>
          <div className="w-full sm:w-1/2 md:w-full lg:w-1/3">Item 2</div>
          <div className="w-full sm:w-full md:w-full lg:w-1/3">Item 3</div>
        </div>
      );
      
      const flexContainer = container.querySelector('.flex');
      expect(flexContainer).toHaveClass('flex-col'); // Mobile: column
      expect(flexContainer).toHaveClass('sm:flex-row');
      expect(flexContainer).toHaveClass('md:flex-col');
      expect(flexContainer).toHaveClass('lg:flex-row');
    });

    it('should handle responsive display utilities', () => {
      const { container } = render(
        <div>
          <div className="inline sm:block md:inline-block lg:flex">
            Responsive Display
          </div>
          <div className="hidden sm:inline md:block lg:hidden xl:flex">
            Complex Display
          </div>
        </div>
      );
      
      const displays = container.querySelectorAll('div > div');
      expect(displays[0]).toHaveClass('inline', 'sm:block', 'md:inline-block', 'lg:flex');
      expect(displays[1]).toHaveClass('hidden', 'sm:inline', 'md:block', 'lg:hidden', 'xl:flex');
    });

    it('should handle responsive overflow behavior', () => {
      const { container } = render(
        <div className="overflow-hidden sm:overflow-visible md:overflow-auto lg:overflow-scroll">
          <div className="whitespace-nowrap sm:whitespace-normal md:whitespace-pre lg:whitespace-pre-wrap">
            Responsive overflow and whitespace
          </div>
        </div>
      );
      
      const overflowDiv = container.querySelector('.overflow-hidden');
      expect(overflowDiv).toHaveClass('sm:overflow-visible');
      expect(overflowDiv).toHaveClass('md:overflow-auto');
      expect(overflowDiv).toHaveClass('lg:overflow-scroll');
      
      const whitespaceDiv = container.querySelector('.whitespace-nowrap');
      expect(whitespaceDiv).toHaveClass('sm:whitespace-normal');
      expect(whitespaceDiv).toHaveClass('md:whitespace-pre');
      expect(whitespaceDiv).toHaveClass('lg:whitespace-pre-wrap');
    });

    it('should handle responsive positioning', () => {
      const { container } = render(
        <div className="relative">
          <div className="static sm:relative md:absolute lg:fixed xl:sticky">
            Responsive Positioning
          </div>
          <div className="top-0 sm:top-4 md:top-8 lg:top-16 left-0 sm:left-4 md:left-8 lg:left-16">
            Responsive Offsets
          </div>
        </div>
      );
      
      const positionDiv = container.querySelector('.static');
      expect(positionDiv).toHaveClass('sm:relative', 'md:absolute', 'lg:fixed', 'xl:sticky');
      
      const offsetDiv = container.querySelector('.top-0');
      expect(offsetDiv).toHaveClass('sm:top-4', 'md:top-8', 'lg:top-16');
      expect(offsetDiv).toHaveClass('left-0', 'sm:left-4', 'md:left-8', 'lg:left-16');
    });
  });

  describe('Responsive Form Layouts', () => {
    it('should handle responsive form layouts', () => {
      const { container } = render(
        <form className="max-w-xs sm:max-w-sm md:max-w-md lg:max-w-lg xl:max-w-xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input 
              className="w-full px-3 py-2 text-sm md:text-base" 
              placeholder="First Name" 
            />
            <input 
              className="w-full px-3 py-2 text-sm md:text-base" 
              placeholder="Last Name" 
            />
          </div>
          <button className="w-full md:w-auto mt-4 px-4 py-2 md:px-6 md:py-3">
            Submit
          </button>
        </form>
      );
      
      const form = container.querySelector('form');
      expect(form).toHaveClass('max-w-xs'); // Mobile
      expect(form).toHaveClass('sm:max-w-sm');
      expect(form).toHaveClass('md:max-w-md');
      expect(form).toHaveClass('lg:max-w-lg');
      expect(form).toHaveClass('xl:max-w-xl');
      
      const button = container.querySelector('button');
      expect(button).toHaveClass('w-full'); // Full width on mobile
      expect(button).toHaveClass('md:w-auto'); // Auto width on desktop
    });
  });
});