import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

// Simple test to check if the test environment works
describe('AssessmentWizard - Simple Test', () => {
  it('should work with basic rendering', () => {
    const div = document.createElement('div');
    div.textContent = 'Hello Test';
    document.body.appendChild(div);

    expect(div.textContent).toBe('Hello Test');

    document.body.removeChild(div);
  });

  it('should work with React Testing Library', () => {
    const TestComponent = () => <div data-testid="test">Test Component</div>;

    render(<TestComponent />);

    expect(screen.getByTestId('test')).toBeInTheDocument();
    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });
});
