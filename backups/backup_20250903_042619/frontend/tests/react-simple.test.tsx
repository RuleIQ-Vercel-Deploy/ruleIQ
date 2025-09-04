import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, it, expect } from 'vitest';

// Test React Testing Library without any complex components
describe('React Testing Library Test', () => {
  it('should render a simple component', () => {
    const SimpleComponent = () => <div data-testid="simple">Hello React</div>;
    render(<SimpleComponent />);
    expect(screen.getByTestId('simple')).toBeInTheDocument();
  });

  it('should handle props', () => {
    const PropsComponent = ({ message }: { message: string }) => (
      <div data-testid="props">{message}</div>
    );
    render(<PropsComponent message="Test Message" />);
    expect(screen.getByTestId('props')).toHaveTextContent('Test Message');
  });

  it('should handle events', () => {
    let clicked = false;
    const ButtonComponent = () => (
      <button
        data-testid="button"
        onClick={() => {
          clicked = true;
        }}
      >
        Click me
      </button>
    );
    render(<ButtonComponent />);

    const button = screen.getByTestId('button');
    button.click();
    expect(clicked).toBe(true);
  });
});
