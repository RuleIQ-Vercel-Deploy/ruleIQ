import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, it, expect } from 'vitest';

// Simple test to check if Dialog component can be imported
describe('Dialog Import Test', () => {
  it('should import Dialog components without error', async () => {
    // Try to import the Dialog components
    const dialogModule = await import('@/components/ui/dialog');

    expect(dialogModule.Dialog).toBeDefined();
    expect(dialogModule.DialogContent).toBeDefined();
    expect(dialogModule.DialogTitle).toBeDefined();
  });

  it('should render a simple div', () => {
    render(<div data-testid="simple-div">Hello World</div>);
    expect(screen.getByTestId('simple-div')).toBeInTheDocument();
  });
});
