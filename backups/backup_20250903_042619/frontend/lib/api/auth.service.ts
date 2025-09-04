// Legacy auth service - replaced by auth store
// This file exists for backward compatibility with existing imports

import { useAuthStore } from '@/lib/stores/auth.store';

export const authService = {
  login: async (email: string, password: string) => {
    return useAuthStore.getState().login(email, password);
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
    return useAuthStore.getState().refreshToken();
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

  updateProfile: async (data: unknown) => {
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
