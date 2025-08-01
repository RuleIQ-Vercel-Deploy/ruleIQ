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
    return useAuthStore.getState().user;
  },
  
  isAuthenticated: () => {
    return useAuthStore.getState().isAuthenticated;
  },
  
  getToken: () => {
    return useAuthStore.getState().tokens?.access_token;
  }
};

export default authService;