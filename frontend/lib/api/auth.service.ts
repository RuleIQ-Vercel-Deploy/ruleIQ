import axios from 'axios';

import { USER_KEY } from '@/config/constants';
import { env } from '@/config/env';
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
    // Backend /token endpoint expects OAuth2PasswordRequestForm (application/x-www-form-urlencoded)
    const formData = new URLSearchParams();
    formData.append('username', credentials.email); // OAuth2 uses 'username' field
    formData.append('password', credentials.password);
    formData.append('grant_type', 'password'); // Required for OAuth2

    try {
      // Call the token endpoint directly using axios (not through apiClient wrapper)
      // because /auth/token returns raw token response, not wrapped in ApiResponse
      const axiosResponse = await axios.post<AuthTokens>(`${env.NEXT_PUBLIC_API_URL}/api/v1/auth/token`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      console.log('Raw axios response:', axiosResponse);
      console.log('Response data:', axiosResponse.data);
      console.log('Response status:', axiosResponse.status);

      // Extract token from direct response (OAuth2 format)
      // The /auth/token endpoint returns tokens directly, not wrapped in a "tokens" object
      const tokens = axiosResponse.data;
      
      // Add detailed validation with better error messaging
      if (!tokens) {
        console.error('No response data received from auth endpoint');
        throw new Error('No response data received from authentication server');
      }

      if (typeof tokens !== 'object') {
        console.error('Invalid response type received:', typeof tokens, tokens);
        throw new Error('Invalid response format from authentication server');
      }
      
      if (!tokens.access_token) {
        console.error('No access token in response. Response keys:', Object.keys(tokens || {}));
        console.error('Full response data:', tokens);
        throw new Error('No access token received from server');
      }

      console.log('Token extracted successfully:', {
        hasAccessToken: !!tokens.access_token,
        hasRefreshToken: !!tokens.refresh_token,
        tokenType: tokens.token_type
      });

      // Get user data using the token (use direct axios call like the token endpoint)
      const userResponse = await axios.get<User>(`${env.NEXT_PUBLIC_API_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
        },
      });

      const authResponse: AuthResponse = {
        user: userResponse.data,
        tokens,
      };

      // Store tokens and user data
      await this.setAuthData(authResponse);

      return authResponse;
    } catch (error) {
      console.error('Login error:', error);
      
      // Enhanced error logging
      if (axios.isAxiosError(error)) {
        console.error('Axios error details:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          url: error.config?.url,
          method: error.config?.method
        });
      }
      
      // Re-throw with better error message
      if (error instanceof Error) {
        throw error;
      }
      
      throw new Error('Login failed');
    }
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
    // Use direct axios call to ensure correct endpoint path
    const token = await this.getAccessToken();
    if (!token) {
      throw new Error('No access token available');
    }
    
    const response = await axios.get<User>(`${env.NEXT_PUBLIC_API_URL}/api/v1/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
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
      refresh_token: refreshToken,
    });

    // Update stored tokens securely
    const expiry = Date.now() + 8 * 60 * 60 * 1000; // 8 hours
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

    const expiry = Date.now() + 8 * 60 * 60 * 1000; // 8 hours
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
