import { AUTH_TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY } from '@/config/constants';

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
    this.setAuthData(response.data);
    
    return response.data;
  }

  /**
   * Register new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    
    // Store tokens and user data
    this.setAuthData(response.data);
    
    return response.data;
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      // Continue with local logout even if API call fails
      console.error('Logout API call failed:', error);
    } finally {
      this.clearAuthData();
      window.location.href = '/auth/login';
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
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<AuthTokens>('/auth/refresh', {
      refresh_token: refreshToken
    });
    
    // Update stored tokens
    if (response.data.access_token) {
      localStorage.setItem(AUTH_TOKEN_KEY, response.data.access_token);
    }
    if (response.data.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, response.data.refresh_token);
    }
    
    return response.data;
  }

  /**
   * Store auth data
   */
  private setAuthData(data: AuthResponse): void {
    if (typeof window === 'undefined') return;
    
    localStorage.setItem(AUTH_TOKEN_KEY, data.tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, data.tokens.refresh_token);
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
   * Clear auth data
   */
  private clearAuthData(): void {
    if (typeof window === 'undefined') return;
    
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
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
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    return !!localStorage.getItem(AUTH_TOKEN_KEY);
  }
}

export const authService = new AuthService();