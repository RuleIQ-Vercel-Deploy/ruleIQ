import { vi } from 'vitest';

// Mock form submission behavior
export const mockFormSubmission = () => {
  // Mock form validation
  HTMLFormElement.prototype.checkValidity = vi.fn().mockReturnValue(true);
  HTMLFormElement.prototype.reportValidity = vi.fn().mockReturnValue(true);
  
  // Mock input validation
  HTMLInputElement.prototype.checkValidity = vi.fn().mockReturnValue(true);
  HTMLInputElement.prototype.setCustomValidity = vi.fn();
  
  // Mock form data
  global.FormData = vi.fn().mockImplementation(() => ({
    append: vi.fn(),
    get: vi.fn(),
    has: vi.fn(),
    set: vi.fn(),
    delete: vi.fn(),
    entries: vi.fn().mockReturnValue([]),
    keys: vi.fn().mockReturnValue([]),
    values: vi.fn().mockReturnValue([])
  }));
};

// Auto-apply form mocks
mockFormSubmission();
