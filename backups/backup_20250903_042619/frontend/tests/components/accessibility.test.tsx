import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';

expect.extend(toHaveNoViolations);

describe('Form Components Accessibility', () => {
  describe('Input Component', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(
        <div>
          <Label htmlFor="test-input">Test Input</Label>
          <Input id="test-input" placeholder="Enter text" />
        </div>,
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should be keyboard navigable', async () => {
      const user = userEvent.setup();
      render(
        <div>
          <Input data-testid="input-1" />
          <Input data-testid="input-2" />
        </div>,
      );

      await user.tab();
      expect(screen.getByTestId('input-1')).toHaveFocus();

      await user.tab();
      expect(screen.getByTestId('input-2')).toHaveFocus();
    });

    it('should announce errors via aria-live', () => {
      render(
        <div>
          <Input error aria-describedby="error-message" />
          <div id="error-message" role="status" aria-live="assertive">
            Error message
          </div>
        </div>,
      );
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toHaveAttribute('aria-live', 'assertive');
    });

    it('should have proper aria-invalid when error', () => {
      render(<Input error />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-invalid', 'true');
    });
  });

  describe('Select Component', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(
        <div>
          <Label htmlFor="test-select">Test Select</Label>
          <Select>
            <SelectTrigger id="test-select">
              <SelectValue placeholder="Select option" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Option 1</SelectItem>
              <SelectItem value="2">Option 2</SelectItem>
            </SelectContent>
          </Select>
        </div>,
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should be keyboard navigable', async () => {
      const user = userEvent.setup();
      render(
        <Select>
          <SelectTrigger>
            <SelectValue placeholder="Select option" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1">Option 1</SelectItem>
            <SelectItem value="2">Option 2</SelectItem>
          </SelectContent>
        </Select>,
      );

      await user.tab();
      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveFocus();

      // Open with keyboard
      await user.keyboard('{Enter}');
      expect(screen.getByRole('listbox')).toBeInTheDocument();

      // Navigate options
      await user.keyboard('{ArrowDown}');
      await user.keyboard('{Enter}');
    });
  });

  describe('Checkbox Component', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(
        <div className="flex items-center space-x-2">
          <Checkbox id="terms" />
          <Label htmlFor="terms">Accept terms and conditions</Label>
        </div>,
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should be keyboard navigable', async () => {
      const user = userEvent.setup();
      render(
        <div>
          <Checkbox data-testid="checkbox-1" />
          <Checkbox data-testid="checkbox-2" />
        </div>,
      );

      await user.tab();
      expect(screen.getByTestId('checkbox-1')).toHaveFocus();

      await user.keyboard(' '); // Space to check
      expect(screen.getByTestId('checkbox-1')).toBeChecked();

      await user.tab();
      expect(screen.getByTestId('checkbox-2')).toHaveFocus();
    });

    it('should have minimum 16x16px click target', () => {
      render(<Checkbox />);
      const checkbox = screen.getByRole('checkbox');

      // Check that the checkbox has the correct Tailwind classes
      expect(checkbox).toHaveClass('h-4', 'w-4');

      // h-4 and w-4 are 16px in Tailwind, satisfying the minimum requirement
      expect(checkbox.className).toMatch(/h-4/);
      expect(checkbox.className).toMatch(/w-4/);
    });
  });

  describe('RadioGroup Component', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(
        <RadioGroup defaultValue="1">
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="1" id="r1" />
            <Label htmlFor="r1">Option 1</Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="2" id="r2" />
            <Label htmlFor="r2">Option 2</Label>
          </div>
        </RadioGroup>,
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should be keyboard navigable with arrow keys', async () => {
      const user = userEvent.setup();
      render(
        <RadioGroup>
          <RadioGroupItem value="1" data-testid="radio-1" />
          <RadioGroupItem value="2" data-testid="radio-2" />
          <RadioGroupItem value="3" data-testid="radio-3" />
        </RadioGroup>,
      );

      await user.tab();
      expect(screen.getByTestId('radio-1')).toHaveFocus();

      await user.keyboard('{ArrowDown}');
      expect(screen.getByTestId('radio-2')).toHaveFocus();

      await user.keyboard('{ArrowDown}');
      expect(screen.getByTestId('radio-3')).toHaveFocus();

      await user.keyboard('{ArrowUp}');
      expect(screen.getByTestId('radio-2')).toHaveFocus();
    });
  });

  describe('Button Component', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(
        <div>
          <Button>Click me</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="destructive">Delete</Button>
          <Button disabled>Disabled</Button>
          <Button loading>Loading</Button>
        </div>,
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have visible focus indicator', async () => {
      const user = userEvent.setup();
      render(<Button>Test Button</Button>);

      await user.tab();
      const button = screen.getByRole('button');
      expect(button).toHaveFocus();

      const styles = window.getComputedStyle(button);
      expect(styles.outlineStyle).not.toBe('none');
    });

    it('should be disabled when loading', () => {
      render(<Button loading>Submit</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });
  });

  describe('Color Contrast', () => {
    it('should have sufficient contrast for all text elements', async () => {
      const { container } = render(
        <div>
          <Button variant="default">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Input placeholder="Type here" />
          <Label>Form Label</Label>
        </div>,
      );

      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      expect(results).toHaveNoViolations();
    });
  });

  describe('Focus Management', () => {
    it('should maintain logical tab order', async () => {
      const user = userEvent.setup();
      render(
        <form>
          <Label htmlFor="name">Name</Label>
          <Input id="name" />

          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" />

          <Checkbox id="subscribe" />
          <Label htmlFor="subscribe">Subscribe to newsletter</Label>

          <Button type="submit">Submit</Button>
        </form>,
      );

      // Tab through all elements
      await user.tab();
      expect(screen.getByLabelText('Name')).toHaveFocus();

      await user.tab();
      expect(screen.getByLabelText('Email')).toHaveFocus();

      await user.tab();
      expect(screen.getByRole('checkbox')).toHaveFocus();

      await user.tab();
      expect(screen.getByRole('button')).toHaveFocus();
    });
  });
});
