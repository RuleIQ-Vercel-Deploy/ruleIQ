/**
 * Basic tests for Select component
 * 
 * Tests core Select component functionality:
 * - Basic rendering and state variants
 * - Custom styling and theming
 * - Accessibility compliance
 */

import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, it, expect } from 'vitest';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  SelectLabel,
  SelectSeparator,
  SelectGroup,
} from '@/components/ui/select';

const BasicSelect = ({ 
  error, 
  success, 
  disabled, 
  defaultValue,
  placeholder = "Select an option",
  className,
}: any) => (
  <Select defaultValue={defaultValue} disabled={disabled}>
    <SelectTrigger 
      error={error} 
      success={success} 
      disabled={disabled}
      className={className}
    >
      <SelectValue placeholder={placeholder} />
    </SelectTrigger>
    <SelectContent>
      <SelectGroup>
        <SelectLabel>Categories</SelectLabel>
        <SelectItem value="option1">Option 1</SelectItem>
        <SelectItem value="option2">Option 2</SelectItem>
        <SelectSeparator />
        <SelectItem value="option3" disabled>
          Option 3 (Disabled)
        </SelectItem>
      </SelectGroup>
    </SelectContent>
  </Select>
);

describe('Select Component', () => {
  describe('Basic Rendering', () => {
    it('renders select trigger with placeholder', () => {
      render(<BasicSelect />);
      
      expect(screen.getByRole('combobox')).toBeInTheDocument();
      expect(screen.getByText('Select an option')).toBeInTheDocument();
    });

    it('renders with default value', () => {
      render(<BasicSelect defaultValue="option1" />);
      
      expect(screen.getByRole('combobox')).toBeInTheDocument();
      expect(screen.getByText('Option 1')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(<BasicSelect className="custom-trigger-class" />);
      
      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveClass('custom-trigger-class');
    });

    it('renders with custom placeholder', () => {
      render(<BasicSelect placeholder="Choose your option" />);
      
      expect(screen.getByText('Choose your option')).toBeInTheDocument();
    });
  });

  describe('State Variants', () => {
    it('applies error state styling', () => {
      render(<BasicSelect error />);
      
      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveClass('border-error', 'focus:border-error', 'focus:ring-error');
    });

    it('applies success state styling', () => {
      render(<BasicSelect success />);
      
      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveClass('border-success', 'focus:border-success', 'focus:ring-success');
    });

    it('handles disabled state', () => {
      render(<BasicSelect disabled />);
      
      const trigger = screen.getByRole('combobox');
      expect(trigger).toBeDisabled();
      expect(trigger).toHaveClass('disabled:cursor-not-allowed', 'disabled:opacity-50');
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(<BasicSelect />);
      
      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveAttribute('aria-expanded', 'false');
      expect(trigger).toHaveAttribute('role', 'combobox');
    });

    it('associates label with select', () => {
      render(
        <div>
          <label htmlFor="test-select">Choose an option</label>
          <Select>
            <SelectTrigger id="test-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="test">Test</SelectItem>
            </SelectContent>
          </Select>
        </div>
      );
      
      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveAccessibleName('Choose an option');
    });

    it('provides accessible description for error state', () => {
      render(
        <div>
          <Select>
            <SelectTrigger error aria-describedby="error-message">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="test">Test</SelectItem>
            </SelectContent>
          </Select>
          <div id="error-message">This field has an error</div>
        </div>
      );
      
      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveAttribute('aria-describedby', 'error-message');
    });
  });

  describe('Theme Integration', () => {
    it('applies ruleIQ theme colors', () => {
      render(<BasicSelect />);
      
      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveClass(
        'bg-eggshell-white',
        'text-oxford-blue',
        'focus:ring-oxford-blue',
        'focus:border-oxford-blue'
      );
    });

    it('includes chevron down icon', () => {
      render(<BasicSelect />);
      
      // Check for the chevron down icon
      expect(screen.getByTestId('chevron-down-icon')).toBeInTheDocument();
    });
  });

  describe('Component Structure', () => {
    it('renders all select subcomponents without errors', () => {
      // Test that all Select components can be rendered together
      render(
        <Select>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Test Group</SelectLabel>
              <SelectItem value="item1">Item 1</SelectItem>
              <SelectSeparator />
              <SelectItem value="item2">Item 2</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      );
      
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    it('handles empty select gracefully', () => {
      render(
        <Select>
          <SelectTrigger>
            <SelectValue placeholder="No options" />
          </SelectTrigger>
          <SelectContent>
            {/* No items */}
          </SelectContent>
        </Select>
      );
      
      expect(screen.getByRole('combobox')).toBeInTheDocument();
      expect(screen.getByText('No options')).toBeInTheDocument();
    });

    it('preserves selection after re-render', () => {
      const { rerender } = render(<BasicSelect defaultValue="option2" />);
      
      expect(screen.getByText('Option 2')).toBeInTheDocument();
      
      rerender(<BasicSelect defaultValue="option2" />);
      
      expect(screen.getByText('Option 2')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles multiple error and success states', () => {
      render(<BasicSelect error success />);
      
      const trigger = screen.getByRole('combobox');
      // Success takes precedence when both are present (last wins in the conditional)
      expect(trigger).toHaveClass('border-success');
    });

    it('handles disabled with other states', () => {
      render(<BasicSelect disabled error />);
      
      const trigger = screen.getByRole('combobox');
      expect(trigger).toBeDisabled();
      expect(trigger).toHaveClass('disabled:opacity-50');
    });
  });
});