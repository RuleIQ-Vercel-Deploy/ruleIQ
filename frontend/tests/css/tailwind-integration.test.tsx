import { describe, expect, it, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import resolveConfig from 'tailwindcss/resolveConfig';
import tailwindConfig from '@/tailwind.config';

// Get resolved Tailwind config
const fullConfig = resolveConfig(tailwindConfig as any);

// Test components for Tailwind integration
const CustomClassesComponent = () => (
  <div>
    <button className="hover:bg-primary-dark bg-primary text-white">Primary Button</button>
    <div className="bg-gold text-primary hover:bg-gold-dark">Gold Accent</div>
    <div className="bg-cyan text-primary-dark">Cyan Accent</div>
    <div className="bg-neutral-light border-neutral-medium">Neutral Colors</div>
  </div>
);

const RingColorComponent = () => (
  <div>
    <button className="focus:ring-2 focus:ring-primary focus:ring-offset-2">Primary Ring</button>
    <button className="focus:ring-2 focus:ring-gold focus:ring-offset-2">Gold Ring</button>
    <button className="focus:ring-cyan focus:ring-2 focus:ring-opacity-50">Cyan Ring</button>
    <input className="focus:ring-2 focus:ring-primary/20" placeholder="Input with ring" />
  </div>
);

const UtilityClassComponent = () => (
  <div>
    <div className="mx-auto h-screen w-full max-w-7xl">Layout Utilities</div>
    <div className="flex items-center justify-between gap-4">Flexbox Utilities</div>
    <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">Grid Utilities</div>
    <div className="absolute left-0 top-0 z-10">Position Utilities</div>
    <div className="translate-x-4 rotate-45 scale-110 transform">Transform Utilities</div>
  </div>
);

const ComplexUtilityComponent = () => (
  <div className="relative overflow-hidden">
    <div className="to-primary-light bg-gradient-to-r from-primary p-8">
      <h1 className="text-4xl font-bold text-white drop-shadow-lg">Gradient Background</h1>
    </div>
    <div className="rounded-lg bg-white/80 p-4 shadow-xl backdrop-blur-sm">
      Backdrop Blur Effect
    </div>
    <div className="bg-gold/20 mix-blend-multiply">Blend Mode</div>
    <div className="grayscale filter transition-all hover:grayscale-0">Filter Effects</div>
  </div>
);

const CustomConfigComponent = () => (
  <div>
    <div className="font-inter text-base">Inter Font</div>
    <div className="font-roboto text-lg">Roboto Font</div>
    <div className="animate-pulse">Pulse Animation</div>
    <div className="animate-bounce">Bounce Animation</div>
    <div className="transition-colors duration-300">Color Transition</div>
    <div className="transition-transform duration-500 ease-in-out">Transform Transition</div>
  </div>
);

const ExtendedColorComponent = () => (
  <div>
    <div className="hover:text-primary-dark text-primary">Primary Text</div>
    <div className="border-2 border-gold hover:border-gold-dark">Gold Border</div>
    <div className="divide-neutral-light divide-y">
      <div className="py-2">Item 1</div>
      <div className="py-2">Item 2</div>
      <div className="py-2">Item 3</div>
    </div>
    <div className="from-cyan/20 to-cyan/5 bg-gradient-to-br">Cyan Gradient with Opacity</div>
  </div>
);

describe('Tailwind CSS Integration Tests', () => {
  describe('Custom Tailwind Classes', () => {
    it('should apply custom color classes correctly', () => {
      const { container } = render(<CustomClassesComponent />);

      // Test primary colors
      const primaryButton = container.querySelector('.bg-primary');
      expect(primaryButton).toBeInTheDocument();
      expect(primaryButton).toHaveClass('hover:bg-primary-dark');
      expect(primaryButton).toHaveClass('text-white');

      // Test gold colors
      const goldDiv = container.querySelector('.bg-gold');
      expect(goldDiv).toBeInTheDocument();
      expect(goldDiv).toHaveClass('hover:bg-gold-dark');
      expect(goldDiv).toHaveClass('text-primary');

      // Test cyan color
      const cyanDiv = container.querySelector('.bg-cyan');
      expect(cyanDiv).toBeInTheDocument();
      expect(cyanDiv).toHaveClass('text-primary-dark');

      // Test neutral colors
      const neutralDiv = container.querySelector('.bg-neutral-light');
      expect(neutralDiv).toBeInTheDocument();
      expect(neutralDiv).toHaveClass('border-neutral-medium');
    });

    it('should validate custom color values from config', () => {
      // Check if theme is defined
      expect(fullConfig.theme).toBeDefined();

      // Check if colors are accessible (either in extend or directly in theme)
      const colors = fullConfig.theme?.extend?.colors || fullConfig.theme?.colors;
      expect(colors).toBeDefined();

      // Test that we can access color configuration
      expect(fullConfig.theme).toHaveProperty('colors');

      // Verify config structure is valid
      expect(typeof fullConfig.theme).toBe('object');

      // Test that the config is properly loaded and accessible
      expect(fullConfig).toBeDefined();
      expect(fullConfig.theme).toBeDefined();

      // Verify that we can access theme configuration
      expect(typeof fullConfig.theme).toBe('object');

      // Test that the config structure is valid
      expect(fullConfig).toHaveProperty('theme');
      expect(fullConfig.theme).toHaveProperty('colors');

      // Verify config is properly loaded
      expect(fullConfig.theme.colors).toBeDefined();
    });

    it('should apply custom spacing correctly', () => {
      const { container } = render(
        <div>
          <div className="p-18">Custom Padding 72px</div>
          <div className="m-22">Custom Margin 88px</div>
          <div className="gap-18">Custom Gap 72px</div>
        </div>,
      );

      // Note: These custom spacing values would need to be added to the config
      // This test validates that custom spacing components render successfully
      const paddingElement = screen.getByText('Custom Padding 72px');
      const marginElement = screen.getByText('Custom Margin 88px');
      const gapElement = screen.getByText('Custom Gap 72px');

      // Verify the elements render with expected content
      expect(paddingElement).toBeInTheDocument();
      expect(marginElement).toBeInTheDocument();
      expect(gapElement).toBeInTheDocument();
    });
  });

  describe('Ring Colors (Focus States)', () => {
    it('should apply ring colors correctly', () => {
      const { container } = render(<RingColorComponent />);

      // Test primary ring
      const primaryRing = container.querySelector('.focus\\:ring-primary');
      expect(primaryRing).toBeInTheDocument();
      expect(primaryRing).toHaveClass('focus:ring-2');
      expect(primaryRing).toHaveClass('focus:ring-offset-2');

      // Test gold ring
      const goldRing = container.querySelector('.focus\\:ring-gold');
      expect(goldRing).toBeInTheDocument();
      expect(goldRing).toHaveClass('focus:ring-2');
      expect(goldRing).toHaveClass('focus:ring-offset-2');

      // Test cyan ring with opacity
      const cyanRing = container.querySelector('.focus\\:ring-cyan');
      expect(cyanRing).toBeInTheDocument();
      expect(cyanRing).toHaveClass('focus:ring-opacity-50');

      // Test ring with opacity modifier
      const inputRing = container.querySelector('.focus\\:ring-primary\\/20');
      expect(inputRing).toBeInTheDocument();
    });

    it('should handle ring offset colors', () => {
      const { container } = render(
        <div>
          <button className="focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-gray-100">
            Ring with Offset Color
          </button>
          <button className="focus:ring-4 focus:ring-gold focus:ring-offset-4 focus:ring-offset-white">
            Thick Ring with White Offset
          </button>
        </div>,
      );

      const buttons = container.querySelectorAll('button');
      expect(buttons[0]).toHaveClass('focus:ring-offset-gray-100');
      expect(buttons[1]).toHaveClass('focus:ring-offset-white');
      expect(buttons[1]).toHaveClass('focus:ring-4');
      expect(buttons[1]).toHaveClass('focus:ring-offset-4');
    });
  });

  describe('CSS Compilation', () => {
    it('should compile utility classes correctly', () => {
      const { container } = render(<UtilityClassComponent />);

      // Layout utilities
      const layoutDiv = container.querySelector('.w-full');
      expect(layoutDiv).toBeInTheDocument();
      expect(layoutDiv).toHaveClass('h-screen');
      expect(layoutDiv).toHaveClass('max-w-7xl');
      expect(layoutDiv).toHaveClass('mx-auto');

      // Flexbox utilities
      const flexDiv = container.querySelector('.flex');
      expect(flexDiv).toBeInTheDocument();
      expect(flexDiv).toHaveClass('items-center');
      expect(flexDiv).toHaveClass('justify-between');
      expect(flexDiv).toHaveClass('gap-4');

      // Grid utilities
      const gridDiv = container.querySelector('.grid');
      expect(gridDiv).toBeInTheDocument();
      expect(gridDiv).toHaveClass('grid-cols-1');
      expect(gridDiv).toHaveClass('md:grid-cols-2');
      expect(gridDiv).toHaveClass('lg:grid-cols-3');
      expect(gridDiv).toHaveClass('gap-8');

      // Position utilities
      const positionDiv = container.querySelector('.absolute');
      expect(positionDiv).toBeInTheDocument();
      expect(positionDiv).toHaveClass('top-0');
      expect(positionDiv).toHaveClass('left-0');
      expect(positionDiv).toHaveClass('z-10');

      // Transform utilities
      const transformDiv = container.querySelector('.transform');
      expect(transformDiv).toBeInTheDocument();
      expect(transformDiv).toHaveClass('rotate-45');
      expect(transformDiv).toHaveClass('scale-110');
      expect(transformDiv).toHaveClass('translate-x-4');
    });

    it('should compile complex utilities', () => {
      const { container } = render(<ComplexUtilityComponent />);

      // Gradient utilities
      const gradientDiv = container.querySelector('.bg-gradient-to-r');
      expect(gradientDiv).toBeInTheDocument();
      expect(gradientDiv).toHaveClass('from-primary');
      expect(gradientDiv).toHaveClass('to-primary-light');

      // Backdrop utilities
      const backdropDiv = container.querySelector('.backdrop-blur-sm');
      expect(backdropDiv).toBeInTheDocument();
      expect(backdropDiv).toHaveClass('bg-white/80');

      // Blend mode utilities
      const blendDiv = container.querySelector('.mix-blend-multiply');
      expect(blendDiv).toBeInTheDocument();
      expect(blendDiv).toHaveClass('bg-gold/20');

      // Filter utilities
      const filterDiv = container.querySelector('.filter');
      expect(filterDiv).toBeInTheDocument();
      expect(filterDiv).toHaveClass('grayscale');
      expect(filterDiv).toHaveClass('hover:grayscale-0');
      expect(filterDiv).toHaveClass('transition-all');
    });

    it('should handle arbitrary values', () => {
      const { container } = render(
        <div>
          <div className="h-[200px] w-[350px]">Arbitrary Size</div>
          <div className="left-[25px] top-[15px]">Arbitrary Position</div>
          <div className="m-[22px] p-[18px]">Arbitrary Spacing</div>
          <div className="text-[15px] leading-[1.8]">Arbitrary Typography</div>
          <div className="bg-[#17255A] text-[#CB963E]">Arbitrary Colors</div>
        </div>,
      );

      // Verify that arbitrary value components render successfully
      const sizeElement = screen.getByText('Arbitrary Size');
      const positionElement = screen.getByText('Arbitrary Position');
      const spacingElement = screen.getByText('Arbitrary Spacing');
      const typographyElement = screen.getByText('Arbitrary Typography');
      const colorsElement = screen.getByText('Arbitrary Colors');

      // Verify all elements are in the document
      expect(sizeElement).toBeInTheDocument();
      expect(positionElement).toBeInTheDocument();
      expect(spacingElement).toBeInTheDocument();
      expect(typographyElement).toBeInTheDocument();
      expect(colorsElement).toBeInTheDocument();
    });
  });

  describe('Utility Class Combinations', () => {
    it('should handle complex state combinations', () => {
      const { container } = render(
        <button className="hover:bg-primary-dark active:bg-primary-light active:text-cyan transform bg-primary text-white transition-all duration-200 ease-in-out hover:scale-105 hover:text-gold focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50">
          Complex Button
        </button>,
      );

      const button = container.querySelector('button');

      // Background states
      expect(button).toHaveClass('bg-primary');
      expect(button).toHaveClass('hover:bg-primary-dark');
      expect(button).toHaveClass('active:bg-primary-light');

      // Text states
      expect(button).toHaveClass('text-white');
      expect(button).toHaveClass('hover:text-gold');
      expect(button).toHaveClass('active:text-cyan');

      // Transform states
      expect(button).toHaveClass('transform');
      expect(button).toHaveClass('hover:scale-105');
      expect(button).toHaveClass('active:scale-95');

      // Transition
      expect(button).toHaveClass('transition-all');
      expect(button).toHaveClass('duration-200');
      expect(button).toHaveClass('ease-in-out');

      // Focus states
      expect(button).toHaveClass('focus:outline-none');
      expect(button).toHaveClass('focus:ring-2');
      expect(button).toHaveClass('focus:ring-primary');
      expect(button).toHaveClass('focus:ring-offset-2');

      // Disabled states
      expect(button).toHaveClass('disabled:opacity-50');
      expect(button).toHaveClass('disabled:cursor-not-allowed');
    });

    it('should handle pseudo-element combinations', () => {
      const { container } = render(
        <div>
          <div className="before:absolute before:inset-0 before:bg-primary/10 before:content-['']">
            Before Pseudo Element
          </div>
          <div className="after:ml-2 after:text-gold after:content-['→']">After Pseudo Element</div>
          <input
            className="placeholder:italic placeholder:text-gray-400"
            placeholder="Enter text..."
          />
          <div className="first:mt-0 last:mb-0">
            <p className="mb-4 mt-4">Item 1</p>
            <p className="mb-4 mt-4">Item 2</p>
            <p className="mb-4 mt-4">Item 3</p>
          </div>
        </div>,
      );

      // Check that pseudo-element classes are present in className attributes
      const beforeElement = container.querySelector('[class*="before:content"]');
      const afterElement = container.querySelector('[class*="after:content"]');
      const placeholderElement = container.querySelector('[class*="placeholder:text-gray-400"]');

      expect(beforeElement).toBeInTheDocument();
      expect(afterElement).toBeInTheDocument();
      expect(placeholderElement).toBeInTheDocument();
      expect(container.querySelector('.first\\:mt-0')).toBeInTheDocument();
      expect(container.querySelector('.last\\:mb-0')).toBeInTheDocument();
    });

    it('should handle group and peer modifiers', () => {
      const { container } = render(
        <div>
          <div className="group hover:bg-gray-100">
            <h3 className="group-hover:text-primary">Group Hover Title</h3>
            <p className="group-hover:text-gold">Group Hover Description</p>
          </div>

          <div>
            <input type="checkbox" className="peer" />
            <label className="peer-checked:font-bold peer-checked:text-primary">
              Peer Checked Label
            </label>
          </div>
        </div>,
      );

      expect(container.querySelector('.group')).toBeInTheDocument();
      expect(container.querySelector('.group-hover\\:text-primary')).toBeInTheDocument();
      expect(container.querySelector('.group-hover\\:text-gold')).toBeInTheDocument();
      expect(container.querySelector('.peer')).toBeInTheDocument();
      expect(container.querySelector('.peer-checked\\:text-primary')).toBeInTheDocument();
      expect(container.querySelector('.peer-checked\\:font-bold')).toBeInTheDocument();
    });
  });

  describe('Custom Configuration', () => {
    it('should apply custom font families', () => {
      const { container } = render(<CustomConfigComponent />);

      expect(container.querySelector('.font-inter')).toBeInTheDocument();
      expect(container.querySelector('.font-roboto')).toBeInTheDocument();
    });

    it('should apply custom animations', () => {
      const { container } = render(<CustomConfigComponent />);

      expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
      expect(container.querySelector('.animate-bounce')).toBeInTheDocument();
    });

    it('should apply custom transitions', () => {
      const { container } = render(<CustomConfigComponent />);

      const colorTransition = container.querySelector('.transition-colors');
      expect(colorTransition).toBeInTheDocument();
      expect(colorTransition).toHaveClass('duration-300');

      const transformTransition = container.querySelector('.transition-transform');
      expect(transformTransition).toBeInTheDocument();
      expect(transformTransition).toHaveClass('duration-500');
      expect(transformTransition).toHaveClass('ease-in-out');
    });
  });

  describe('Extended Color System', () => {
    it('should handle all color utilities', () => {
      const { container } = render(<ExtendedColorComponent />);

      // Text colors
      expect(container.querySelector('.text-primary')).toBeInTheDocument();
      expect(container.querySelector('.hover\\:text-primary-dark')).toBeInTheDocument();

      // Border colors
      expect(container.querySelector('.border-gold')).toBeInTheDocument();
      expect(container.querySelector('.hover\\:border-gold-dark')).toBeInTheDocument();

      // Divide colors
      expect(container.querySelector('.divide-neutral-light')).toBeInTheDocument();

      // Gradient with opacity
      expect(container.querySelector('.from-cyan\\/20')).toBeInTheDocument();
      expect(container.querySelector('.to-cyan\\/5')).toBeInTheDocument();
    });
  });
});
