// Legacy auth service - replaced by auth store
// This file exists for backward compatibility with existing imports

import { useAuthStore } from '@/lib/stores/auth.store';
import type { User } from '@/types/auth';

export const authService = {
  login: async (params: { email: string; password: string } | string, password?: string) => {
    // Handle both old and new signatures
    if (typeof params === 'string') {
      // Old signature: login(email, password)
      return useAuthStore.getState().login({ email: params, password: password!, rememberMe: false });
    }
    // New signature: login({ email, password })
    return useAuthStore.getState().login(params);
  },

  register: async (email: string, password: string, fullName?: string) => {
    return useAuthStore.getState().register(email, password, fullName);
  },

  logout: () => {
    return useAuthStore.getState().logout();
  },

  getCurrentUser: () => {
    return useAuthStore.getState().getCurrentUser();
  },

  isAuthenticated: () => {
    return useAuthStore.getState().isAuthenticated;
  },

  getToken: () => {
    return useAuthStore.getState().getToken();
  },

  refreshToken: async () => {
    return useAuthStore.getState().refreshTokens();
  },

  // Add post method for token refresh
  post: async (url: string, data?: any) => {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }
    return { data: await response.json() };
  },

  checkAuthStatus: async () => {
    return useAuthStore.getState().checkAuthStatus();
  },

  initialize: async () => {
    return useAuthStore.getState().initialize();
  },

  requestPasswordReset: async (email: string) => {
    return useAuthStore.getState().requestPasswordReset(email);
  },

  resetPassword: async (token: string, password: string) => {
    return useAuthStore.getState().resetPassword(token, password);
  },

  verifyEmail: async (token: string) => {
    return useAuthStore.getState().verifyEmail(token);
  },

  updateProfile: async (data: Partial<User>) => {
    return useAuthStore.getState().updateProfile(data);
  },

  changePassword: async (currentPassword: string, newPassword: string) => {
    return useAuthStore.getState().changePassword(currentPassword, newPassword);
  },

  clearError: () => {
    return useAuthStore.getState().clearError();
  },

  getUser: () => {
    return useAuthStore.getState().user;
  },

  getTokens: () => {
    return useAuthStore.getState().tokens;
  },

  getError: () => {
    return useAuthStore.getState().error;
  },

  isLoading: () => {
    return useAuthStore.getState().isLoading;
  },
};

export default authService;
