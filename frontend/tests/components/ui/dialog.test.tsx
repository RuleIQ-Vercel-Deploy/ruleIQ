/**
 * Basic tests for Dialog component
 * 
 * Tests core dialog functionality:
 * - Dialog structure and rendering
 * - Component integration
 * - Accessibility compliance
 * - Custom styling
 */

import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, it, expect } from 'vitest';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from '@/components/ui/dialog';

const BasicDialog = ({ 
  open = false,
  includeDescription = false,
  includeFooter = false,
  customClassName,
}: {
  open?: boolean;
  includeDescription?: boolean;
  includeFooter?: boolean;
  customClassName?: string;
}) => (
  <Dialog open={open}>
    <DialogTrigger asChild>
      <button>Open Dialog</button>
    </DialogTrigger>
    <DialogContent className={customClassName}>
      <DialogHeader>
        <DialogTitle>Dialog Title</DialogTitle>
        {includeDescription && (
          <DialogDescription>
            This is a dialog description explaining what this dialog does.
          </DialogDescription>
        )}
      </DialogHeader>
      
      <div className="dialog-body">
        <p>Dialog content goes here.</p>
      </div>

      {includeFooter && (
        <DialogFooter>
          <DialogClose asChild>
            <button>Cancel</button>
          </DialogClose>
          <button>Confirm</button>
        </DialogFooter>
      )}
    </DialogContent>
  </Dialog>
);

describe('Dialog Components', () => {
  describe('Basic Rendering', () => {
    it('renders dialog trigger', () => {
      render(<BasicDialog />);

      expect(screen.getByRole('button', { name: 'Open Dialog' })).toBeInTheDocument();
    });

    it('renders dialog content when open', () => {
      render(<BasicDialog open />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Dialog Title')).toBeInTheDocument();
      expect(screen.getByText('Dialog content goes here.')).toBeInTheDocument();
    });

    it('renders dialog with description when enabled', () => {
      render(<BasicDialog open includeDescription />);

      expect(screen.getByText('This is a dialog description explaining what this dialog does.')).toBeInTheDocument();
    });

    it('renders dialog with footer when enabled', () => {
      render(<BasicDialog open includeFooter />);

      expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Confirm' })).toBeInTheDocument();
    });

    it('does not render dialog content when closed', () => {
      render(<BasicDialog open={false} />);

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      expect(screen.queryByText('Dialog Title')).not.toBeInTheDocument();
    });
  });

  describe('Dialog Structure', () => {
    it('includes close button in dialog content', () => {
      render(<BasicDialog open />);

      const closeButton = screen.getByRole('button', { name: 'Close' });
      expect(closeButton).toBeInTheDocument();
    });

    it('applies correct CSS classes to dialog components', () => {
      render(<BasicDialog open includeDescription includeFooter />);

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveClass('fixed', 'left-[50%]', 'top-[50%]', 'z-50');

      const header = screen.getByText('Dialog Title').closest('.flex');
      expect(header).toHaveClass('flex-col', 'space-y-1.5');

      const footer = screen.getByRole('button', { name: 'Cancel' }).closest('.flex');
      expect(footer).toHaveClass('flex-col-reverse', 'sm:flex-row');
    });

    it('applies custom className to DialogContent', () => {
      render(<BasicDialog open customClassName="custom-dialog" />);

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveClass('custom-dialog');
    });
  });

  describe('Dialog Components', () => {
    it('renders DialogHeader with correct structure', () => {
      render(<BasicDialog open />);

      const title = screen.getByText('Dialog Title');
      const header = title.closest('.flex');
      
      expect(header).toBeInTheDocument();
      expect(header).toHaveClass('flex', 'flex-col', 'space-y-1.5');
      expect(header).toContainElement(title);
    });

    it('renders DialogTitle with correct styling', () => {
      render(<BasicDialog open />);

      const title = screen.getByText('Dialog Title');
      expect(title).toHaveClass('text-lg', 'font-semibold');
    });

    it('renders DialogDescription with correct styling', () => {
      render(<BasicDialog open includeDescription />);

      const description = screen.getByText('This is a dialog description explaining what this dialog does.');
      expect(description).toHaveClass('text-sm', 'text-muted-foreground');
    });

    it('renders DialogFooter with correct layout', () => {
      render(<BasicDialog open includeFooter />);

      const footer = screen.getByRole('button', { name: 'Cancel' }).closest('.flex');
      expect(footer).toHaveClass('flex', 'flex-col-reverse', 'sm:flex-row', 'sm:justify-end');
    });
  });

  describe('Accessibility', () => {
    it('provides proper dialog role', () => {
      render(<BasicDialog open />);

      const dialog = screen.getByRole('dialog');
      expect(dialog).toBeInTheDocument();
    });

    it('associates title with dialog', () => {
      render(<BasicDialog open />);

      const dialog = screen.getByRole('dialog');
      const title = screen.getByText('Dialog Title');
      
      expect(dialog).toHaveAttribute('aria-labelledby');
      expect(title).toHaveAttribute('id');
    });

    it('associates description with dialog when present', () => {
      render(<BasicDialog open includeDescription />);

      const dialog = screen.getByRole('dialog');
      const description = screen.getByText('This is a dialog description explaining what this dialog does.');
      
      expect(dialog).toHaveAttribute('aria-describedby');
      expect(description).toHaveAttribute('id');
    });

    it('provides accessible close button', () => {
      render(<BasicDialog open />);

      const closeButton = screen.getByRole('button', { name: 'Close' });
      expect(closeButton).toBeInTheDocument();
      expect(closeButton).toHaveAccessibleName('Close');
    });

    it('includes screen reader text for close button', () => {
      render(<BasicDialog open />);

      expect(screen.getByText('Close')).toHaveClass('sr-only');
    });
  });

  describe('Component Integration', () => {
    it('integrates all dialog components correctly', () => {
      render(<BasicDialog open includeDescription includeFooter />);

      const dialog = screen.getByRole('dialog');
      const title = screen.getByText('Dialog Title');
      const description = screen.getByText('This is a dialog description explaining what this dialog does.');
      const content = screen.getByText('Dialog content goes here.');
      const cancelButton = screen.getByRole('button', { name: 'Cancel' });
      const confirmButton = screen.getByRole('button', { name: 'Confirm' });
      const closeButton = screen.getByRole('button', { name: 'Close' });

      expect(dialog).toContainElement(title);
      expect(dialog).toContainElement(description);
      expect(dialog).toContainElement(content);
      expect(dialog).toContainElement(cancelButton);
      expect(dialog).toContainElement(confirmButton);
      expect(dialog).toContainElement(closeButton);
    });

    it('maintains proper component hierarchy', () => {
      render(<BasicDialog open includeDescription includeFooter />);

      const title = screen.getByText('Dialog Title');
      const description = screen.getByText('This is a dialog description explaining what this dialog does.');
      const header = title.closest('.flex');

      // Title and description should be in the same header
      expect(header).toContainElement(title);
      expect(header).toContainElement(description);

      // Footer should contain both buttons
      const footer = screen.getByRole('button', { name: 'Cancel' }).closest('.flex');
      const confirmButton = screen.getByRole('button', { name: 'Confirm' });
      expect(footer).toContainElement(confirmButton);
    });
  });

  describe('Custom Styling', () => {
    it('accepts custom className on DialogContent', () => {
      render(<BasicDialog open customClassName="my-custom-dialog" />);

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveClass('my-custom-dialog');
      // Should also maintain default classes
      expect(dialog).toHaveClass('fixed', 'left-[50%]', 'top-[50%]');
    });

    it('allows custom className on DialogHeader', () => {
      const CustomHeaderDialog = () => (
        <Dialog open>
          <DialogContent>
            <DialogHeader className="custom-header">
              <DialogTitle>Custom Header</DialogTitle>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      );

      render(<CustomHeaderDialog />);

      const header = screen.getByText('Custom Header').closest('.custom-header');
      expect(header).toBeInTheDocument();
      expect(header).toHaveClass('flex', 'flex-col', 'custom-header');
    });

    it('allows custom className on DialogFooter', () => {
      const CustomFooterDialog = () => (
        <Dialog open>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Title</DialogTitle>
            </DialogHeader>
            <DialogFooter className="custom-footer">
              <button>Action</button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      );

      render(<CustomFooterDialog />);

      const footer = screen.getByRole('button', { name: 'Action' }).closest('.custom-footer');
      expect(footer).toBeInTheDocument();
      expect(footer).toHaveClass('flex', 'custom-footer');
    });

    it('allows custom className on DialogTitle', () => {
      const CustomTitleDialog = () => (
        <Dialog open>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="custom-title">Custom Title</DialogTitle>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      );

      render(<CustomTitleDialog />);

      const title = screen.getByText('Custom Title');
      expect(title).toHaveClass('text-lg', 'font-semibold', 'custom-title');
    });

    it('allows custom className on DialogDescription', () => {
      const CustomDescriptionDialog = () => (
        <Dialog open>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Title</DialogTitle>
              <DialogDescription className="custom-description">
                Custom description text
              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      );

      render(<CustomDescriptionDialog />);

      const description = screen.getByText('Custom description text');
      expect(description).toHaveClass('text-sm', 'text-muted-foreground', 'custom-description');
    });
  });

  describe('Edge Cases', () => {
    it('handles dialog without description', () => {
      render(<BasicDialog open includeDescription={false} />);

      expect(screen.getByText('Dialog Title')).toBeInTheDocument();
      expect(screen.queryByText(/This is a dialog description/)).not.toBeInTheDocument();
    });

    it('handles dialog without footer', () => {
      render(<BasicDialog open includeFooter={false} />);

      expect(screen.getByText('Dialog Title')).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: 'Confirm' })).not.toBeInTheDocument();
    });

    it('handles minimal dialog structure', () => {
      const MinimalDialog = () => (
        <Dialog open>
          <DialogContent>
            <DialogTitle>Minimal</DialogTitle>
          </DialogContent>
        </Dialog>
      );

      render(<MinimalDialog />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Minimal')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Close' })).toBeInTheDocument();
    });

    it('handles empty dialog content', () => {
      const EmptyDialog = () => (
        <Dialog open>
          <DialogContent>
            {/* Empty content */}
          </DialogContent>
        </Dialog>
      );

      render(<EmptyDialog />);

      const dialog = screen.getByRole('dialog');
      expect(dialog).toBeInTheDocument();
      // Should still have close button
      expect(screen.getByRole('button', { name: 'Close' })).toBeInTheDocument();
    });

    it('maintains component stability across re-renders', () => {
      const { rerender } = render(<BasicDialog open />);

      const initialDialog = screen.getByRole('dialog');
      const initialTitle = screen.getByText('Dialog Title');

      rerender(<BasicDialog open includeDescription />);

      // Components should still be present
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Dialog Title')).toBeInTheDocument();
      expect(screen.getByText('This is a dialog description explaining what this dialog does.')).toBeInTheDocument();
    });
  });
});