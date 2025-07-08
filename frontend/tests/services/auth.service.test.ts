import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';

import { authService } from '@/lib/api/auth.service';
import { apiClient } from '@/lib/api/client';

// Mock the API client
vi.mock('@/lib/api/client', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
    getToken: vi.fn(),
  },
}));

describe('AuthService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          user: {
            id: '1',
            email: 'test@example.com',
            full_name: 'Test User',
            is_active: true,
          },
        },
        status: 200,
        message: 'Success',
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      };

      const result = await authService.login(credentials);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/login', credentials);
      expect(result).toEqual(mockResponse.data);
    });

    it('should throw error for invalid credentials', async () => {
      const mockError = new Error('Invalid credentials');
      vi.mocked(apiClient.post).mockRejectedValue(mockError);

      const credentials = {
        email: 'invalid@example.com',
        password: 'wrongpassword',
      };

      await expect(authService.login(credentials)).rejects.toThrow('Invalid credentials');
    });

    it('should handle network errors', async () => {
      const networkError = new Error('Network error');
      vi.mocked(apiClient.post).mockRejectedValue(networkError);

      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      };

      await expect(authService.login(credentials)).rejects.toThrow('Network error');
    });
  });

  describe('register', () => {
    it('should register new user successfully', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          user: {
            id: '1',
            email: 'newuser@example.com',
            full_name: 'New User',
            is_active: true,
          },
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const userData = {
        email: 'newuser@example.com',
        password: 'password123',
        full_name: 'New User',
        company: 'Test Company',
      };

      const result = await authService.register(userData);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/register', userData);
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle duplicate email error', async () => {
      const duplicateError = new Error('Email already exists');
      vi.mocked(apiClient.post).mockRejectedValue(duplicateError);

      const userData = {
        email: 'existing@example.com',
        password: 'password123',
        full_name: 'Test User',
      };

      await expect(authService.register(userData)).rejects.toThrow('Email already exists');
    });

    it('should validate required fields', async () => {
      const validationError = new Error('Validation failed');
      vi.mocked(apiClient.post).mockRejectedValue(validationError);

      const incompleteData = {
        email: 'test@example.com',
        // Missing password and full_name
      };

      await expect(authService.register(incompleteData as any)).rejects.toThrow('Validation failed');
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      const mockResponse = { data: { message: 'Logged out successfully' } };
      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);
      vi.mocked(apiClient.getToken).mockResolvedValue('mock-token');

      await authService.logout();

      expect(apiClient.post).toHaveBeenCalledWith('/auth/logout');
    });

    it('should handle logout errors gracefully', async () => {
      const logoutError = new Error('Logout failed');
      vi.mocked(apiClient.post).mockRejectedValue(logoutError);

      // Should not throw error even if logout fails
      await expect(authService.logout()).resolves.toBeUndefined();
    });
  });

  describe('refreshToken', () => {
    it('should refresh token successfully', async () => {
      const mockResponse = {
        data: {
          access_token: 'new-access-token',
          refresh_token: 'new-refresh-token',
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const result = await authService.refreshToken();

      expect(apiClient.post).toHaveBeenCalledWith('/auth/refresh');
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle expired refresh token', async () => {
      const expiredError = new Error('Refresh token expired');
      vi.mocked(apiClient.post).mockRejectedValue(expiredError);

      await expect(authService.refreshToken()).rejects.toThrow('Refresh token expired');
    });
  });

  describe('getCurrentUser', () => {
    it('should get current user successfully', async () => {
      const mockResponse = {
        data: {
          id: '1',
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
        },
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await authService.getCurrentUser();

      expect(apiClient.get).toHaveBeenCalledWith('/users/me');
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle unauthorized access', async () => {
      const unauthorizedError = new Error('Unauthorized');
      vi.mocked(apiClient.get).mockRejectedValue(unauthorizedError);

      await expect(authService.getCurrentUser()).rejects.toThrow('Unauthorized');
    });
  });

  describe('requestPasswordReset', () => {
    it('should request password reset successfully', async () => {
      const mockResponse = { data: { message: 'Password reset email sent' } };
      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      await authService.requestPasswordReset('test@example.com');

      expect(apiClient.post).toHaveBeenCalledWith('/auth/request-password-reset', {
        email: 'test@example.com',
      });
    });

    it('should handle non-existent email', async () => {
      const notFoundError = new Error('Email not found');
      vi.mocked(apiClient.post).mockRejectedValue(notFoundError);

      await expect(authService.requestPasswordReset('nonexistent@example.com')).rejects.toThrow('Email not found');
    });
  });

  describe('resetPassword', () => {
    it('should reset password successfully', async () => {
      const mockResponse = { data: { message: 'Password reset successfully' } };
      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      await authService.resetPassword('reset-token', 'newpassword123');

      expect(apiClient.post).toHaveBeenCalledWith('/auth/reset-password', {
        token: 'reset-token',
        password: 'newpassword123',
      });
    });

    it('should handle invalid reset token', async () => {
      const invalidTokenError = new Error('Invalid or expired token');
      vi.mocked(apiClient.post).mockRejectedValue(invalidTokenError);

      await expect(authService.resetPassword('invalid-token', 'newpassword')).rejects.toThrow('Invalid or expired token');
    });
  });

  describe('verifyEmail', () => {
    it('should verify email successfully', async () => {
      const mockResponse = { data: { message: 'Email verified successfully' } };
      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      await authService.verifyEmail('verification-token');

      expect(apiClient.post).toHaveBeenCalledWith('/auth/verify-email', {
        token: 'verification-token',
      });
    });

    it('should handle invalid verification token', async () => {
      const invalidTokenError = new Error('Invalid verification token');
      vi.mocked(apiClient.post).mockRejectedValue(invalidTokenError);

      await expect(authService.verifyEmail('invalid-token')).rejects.toThrow('Invalid verification token');
    });
  });

  describe('updateProfile', () => {
    it('should update user profile successfully', async () => {
      const mockResponse = {
        data: {
          id: '1',
          email: 'test@example.com',
          full_name: 'Updated Name',
          is_active: true,
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const updateData = {
        full_name: 'Updated Name',
        company: 'New Company',
      };

      const result = await authService.updateProfile(updateData);

      expect(apiClient.post).toHaveBeenCalledWith('/users/me', updateData);
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('changePassword', () => {
    it('should change password successfully', async () => {
      const mockResponse = { data: { message: 'Password changed successfully' } };
      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const passwordData = {
        current_password: 'oldpassword',
        new_password: 'newpassword123',
      };

      await authService.changePassword(passwordData);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/change-password', passwordData);
    });

    it('should handle incorrect current password', async () => {
      const incorrectPasswordError = new Error('Current password is incorrect');
      vi.mocked(apiClient.post).mockRejectedValue(incorrectPasswordError);

      const passwordData = {
        current_password: 'wrongpassword',
        new_password: 'newpassword123',
      };

      await expect(authService.changePassword(passwordData)).rejects.toThrow('Current password is incorrect');
    });
  });
});
