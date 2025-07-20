import { USER_KEY } from '@/config/constants';
import SecureStorage from '@/lib/utils/secure-storage';

import { apiClient } from './client';

import type { AuthTokens, User } from '@/types/global';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  company_name: string;
  company_size: string;
  industry: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

class AuthService {
  /**
   * Login user
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    // Backend expects FormData for login
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await apiClient.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Store tokens and user data
    await this.setAuthData(response.data);
    
    return response.data;
  }

  /**
   * Register new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    
    // Store tokens and user data
    await this.setAuthData(response.data);
    
    return response.data;
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      // Only attempt API logout if we have a token
      const token = await apiClient.getToken();
      if (token) {
        await apiClient.post('/auth/logout');
      }
    } catch (error) {
      // Continue with local logout even if API call fails
      console.warn('Logout API call failed, continuing with local logout:', error);
    } finally {
      // Always clear local auth data
      this.clearAuthData();

      // Redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login';
      }
    }
  }

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  }

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await apiClient.patch<User>('/auth/profile', data);
    
    // Update stored user data
    this.setUser(response.data);
    
    return response.data;
  }

  /**
   * Change password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    await apiClient.post('/auth/forgot-password', { email });
  }

  /**
   * Reset password with token
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    });
  }

  /**
   * Verify email with token
   */
  async verifyEmail(token: string): Promise<void> {
    await apiClient.post('/auth/verify-email', { token });
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<AuthTokens> {
    const refreshToken = SecureStorage.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<AuthTokens>('/auth/refresh', {
      refresh_token: refreshToken
    });
    
    // Update stored tokens securely
    const expiry = Date.now() + (8 * 60 * 60 * 1000); // 8 hours
    if (response.data.access_token) {
      await SecureStorage.setAccessToken(response.data.access_token, { expiry });
    }
    if (response.data.refresh_token) {
      SecureStorage.setRefreshToken(response.data.refresh_token, expiry);
    }
    
    return response.data;
  }

  /**
   * Store auth data securely
   */
  private async setAuthData(data: AuthResponse): Promise<void> {
    if (typeof window === 'undefined') return;
    
    const expiry = Date.now() + (8 * 60 * 60 * 1000); // 8 hours
    await SecureStorage.setAccessToken(data.tokens.access_token, { expiry });
    SecureStorage.setRefreshToken(data.tokens.refresh_token, expiry);
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  }

  /**
   * Store user data
   */
  private setUser(user: User): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  /**
   * Clear auth data from secure storage
   */
  private clearAuthData(): void {
    if (typeof window === 'undefined') return;
    
    SecureStorage.clearAll();
    localStorage.removeItem(USER_KEY);
  }

  /**
   * Get stored user
   */
  getStoredUser(): User | null {
    if (typeof window === 'undefined') return null;
    
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    if (typeof window === 'undefined') return false;
    try {
      const token = await SecureStorage.getAccessToken();
      return !!token && !SecureStorage.isSessionExpired();
    } catch (error) {
      return false;
    }
  }

  /**
   * Get access token from secure storage
   */
  async getAccessToken(): Promise<string | null> {
    try {
      return await SecureStorage.getAccessToken();
    } catch (error) {
      return null;
    }
  }
}

export const authService = new AuthService();