// Re-export all utilities for easier imports
export * from './test-utils';
export * from './assessment-test-utils';
export * from './memory-leak-detector';

// Re-export testing library exports for convenience
export { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
export { userEvent } from '@testing-library/user-event';
