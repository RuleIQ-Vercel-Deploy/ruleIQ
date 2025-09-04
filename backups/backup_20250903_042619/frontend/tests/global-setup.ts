import { setupAuthMocks } from './mocks/auth-setup';
import { beforeEach } from 'vitest';

// Global setup for all tests
beforeEach(() => {
  setupAuthMocks();
});
