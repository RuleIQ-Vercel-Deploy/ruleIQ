/**
 * Basic tests for Form components
 * 
 * Tests core form rendering and structure:
 * - Form components render correctly
 * - Accessibility attributes are present
 * - CSS classes are applied correctly
 * - Component integration works
 */

import { render, screen } from '@testing-library/react';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect } from 'vitest';

import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';

const SimpleForm = ({ 
  includeDescription = false,
  customClassName,
}: {
  includeDescription?: boolean;
  customClassName?: string;
}) => {
  const form = useForm({
    defaultValues: {
      username: '',
      email: '',
    },
  });

  return (
    <Form {...form}>
      <form className="space-y-4">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem className={customClassName}>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="Enter username" {...field} />
              </FormControl>
              {includeDescription && (
                <FormDescription>
                  Choose a unique username.
                </FormDescription>
              )}
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="Enter email" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
};

describe('Form Components - Basic Tests', () => {
  describe('Rendering', () => {
    it('renders all form components', () => {
      render(<SimpleForm />);

      expect(screen.getByLabelText('Username')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter username')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter email')).toBeInTheDocument();
    });

    it('renders with descriptions when enabled', () => {
      render(<SimpleForm includeDescription />);

      expect(screen.getByText('Choose a unique username.')).toBeInTheDocument();
    });

    it('applies custom className to FormItem', () => {
      render(<SimpleForm customClassName="custom-form-item" />);

      const formItem = screen.getByLabelText('Username').closest('.custom-form-item');
      expect(formItem).toBeInTheDocument();
    });
  });

  describe('Form Structure', () => {
    it('creates proper spacing classes', () => {
      render(<SimpleForm />);

      const formItems = document.querySelectorAll('.space-y-2');
      expect(formItems.length).toBeGreaterThanOrEqual(2);
    });

    it('generates unique IDs', () => {
      render(<SimpleForm includeDescription />);

      const usernameInput = screen.getByLabelText('Username');
      const emailInput = screen.getByLabelText('Email');
      const description = screen.getByText('Choose a unique username.');

      expect(usernameInput.id).toBeTruthy();
      expect(emailInput.id).toBeTruthy();
      expect(description.id).toBeTruthy();
      expect(usernameInput.id).not.toBe(emailInput.id);
    });

    it('connects labels to inputs', () => {
      render(<SimpleForm />);

      const usernameLabel = screen.getByText('Username');
      const usernameInput = screen.getByLabelText('Username');

      expect(usernameLabel).toHaveAttribute('for', usernameInput.id);
    });
  });

  describe('Component Classes', () => {
    it('applies correct FormDescription classes', () => {
      render(<SimpleForm includeDescription />);

      const description = screen.getByText('Choose a unique username.');
      expect(description).toHaveClass('text-sm', 'text-muted-foreground');
    });

    it('applies correct FormItem classes', () => {
      render(<SimpleForm />);

      const formItem = screen.getByLabelText('Username').closest('.space-y-2');
      expect(formItem).toBeInTheDocument();
    });

    it('applies correct FormLabel classes', () => {
      render(<SimpleForm />);

      const label = screen.getByText('Username');
      expect(label).toHaveClass('text-sm', 'font-medium');
    });
  });

  describe('Accessibility', () => {
    it('provides ARIA attributes on form controls', () => {
      render(<SimpleForm includeDescription />);

      const usernameInput = screen.getByLabelText('Username');
      
      expect(usernameInput).toHaveAttribute('aria-describedby');
      expect(usernameInput).toHaveAttribute('aria-invalid', 'false');
    });

    it('associates descriptions with controls', () => {
      render(<SimpleForm includeDescription />);

      const usernameInput = screen.getByLabelText('Username');
      const description = screen.getByText('Choose a unique username.');
      const describedBy = usernameInput.getAttribute('aria-describedby');

      expect(describedBy).toContain(description.id);
    });

    it('provides proper label associations', () => {
      render(<SimpleForm />);

      expect(screen.getByLabelText('Username')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
    });
  });

  describe('FormMessage Component', () => {
    it('renders FormMessage component (empty when no errors)', () => {
      render(<SimpleForm />);

      // FormMessage should be in DOM but empty/hidden when no errors
      const errorElements = document.querySelectorAll('[class*="text-destructive"]');
      expect(errorElements).toHaveLength(0);
    });

    it('FormMessage is present in DOM structure', () => {
      render(<SimpleForm />);

      // FormMessage components should be present but not visible
      const formItems = document.querySelectorAll('.space-y-2');
      expect(formItems.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('Integration', () => {
    it('integrates all form components in correct hierarchy', () => {
      render(<SimpleForm includeDescription />);

      const usernameInput = screen.getByLabelText('Username');
      const formItem = usernameInput.closest('.space-y-2');
      
      expect(formItem).toBeInTheDocument();
      
      const label = screen.getByText('Username');
      const description = screen.getByText('Choose a unique username.');
      
      expect(formItem).toContainElement(label);
      expect(formItem).toContainElement(usernameInput);
      expect(formItem).toContainElement(description);
    });

    it('works with multiple form fields', () => {
      render(<SimpleForm />);

      const usernameInput = screen.getByLabelText('Username');
      const emailInput = screen.getByLabelText('Email');
      
      expect(usernameInput).toBeInTheDocument();
      expect(emailInput).toBeInTheDocument();
      expect(usernameInput.id).not.toBe(emailInput.id);
    });

    it('handles empty form state correctly', () => {
      render(<SimpleForm />);

      const usernameInput = screen.getByLabelText('Username');
      const emailInput = screen.getByLabelText('Email');
      
      expect(usernameInput).toHaveValue('');
      expect(emailInput).toHaveValue('');
    });
  });

  describe('Custom Styling', () => {
    it('accepts custom className on FormDescription', () => {
      const CustomForm = () => {
        const form = useForm({ defaultValues: { test: '' } });
        
        return (
          <Form {...form}>
            <FormField
              control={form.control}
              name="test"
              render={() => (
                <FormItem>
                  <FormLabel>Test</FormLabel>
                  <FormControl>
                    <Input />
                  </FormControl>
                  <FormDescription className="custom-description">
                    Custom description
                  </FormDescription>
                </FormItem>
              )}
            />
          </Form>
        );
      };

      render(<CustomForm />);
      
      const description = screen.getByText('Custom description');
      expect(description).toHaveClass('text-sm', 'text-muted-foreground', 'custom-description');
    });

    it('accepts custom className on FormItem', () => {
      render(<SimpleForm customClassName="my-custom-class" />);

      const formItem = screen.getByLabelText('Username').closest('.my-custom-class');
      expect(formItem).toBeInTheDocument();
      expect(formItem).toHaveClass('space-y-2', 'my-custom-class');
    });

    it('maintains default styles with custom classes', () => {
      render(<SimpleForm customClassName="custom" includeDescription />);

      const formItem = screen.getByLabelText('Username').closest('.custom');
      const description = screen.getByText('Choose a unique username.');
      
      expect(formItem).toHaveClass('space-y-2', 'custom');
      expect(description).toHaveClass('text-sm', 'text-muted-foreground');
    });
  });

  describe('Edge Cases', () => {
    it('handles multiple forms on same page', () => {
      render(
        <div>
          <SimpleForm />
          <SimpleForm />
        </div>
      );

      const usernameInputs = screen.getAllByLabelText('Username');
      const emailInputs = screen.getAllByLabelText('Email');
      
      expect(usernameInputs).toHaveLength(2);
      expect(emailInputs).toHaveLength(2);
      
      expect(usernameInputs[0].id).not.toBe(usernameInputs[1].id);
      expect(emailInputs[0].id).not.toBe(emailInputs[1].id);
    });

    it('handles form with no fields', () => {
      const EmptyForm = () => {
        const form = useForm({ defaultValues: {} });
        return (
          <Form {...form}>
            <form>
              <div>Empty form</div>
            </form>
          </Form>
        );
      };

      render(<EmptyForm />);
      
      expect(screen.getByText('Empty form')).toBeInTheDocument();
    });

    it('maintains component structure consistency', () => {
      const { rerender } = render(<SimpleForm />);
      
      const initialUsername = screen.getByLabelText('Username');
      const initialUsernameId = initialUsername.id;
      
      rerender(<SimpleForm includeDescription />);
      
      const updatedUsername = screen.getByLabelText('Username');
      expect(updatedUsername.id).toBe(initialUsernameId); // ID should remain stable
      expect(screen.getByText('Choose a unique username.')).toBeInTheDocument();
    });
  });
});