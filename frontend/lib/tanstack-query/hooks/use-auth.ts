import { useMutation, useQueryClient } from '@tanstack/react-query';


import { authService } from '@/lib/api/auth.service';
import { useAuthStore } from '@/lib/stores/auth.store';

import { type BaseMutationOptions, getErrorMessage } from './base';

import type { LoginRequest, SignupRequest, User } from '@/types/api';

// Hook for login
export function useLogin(
  options?: BaseMutationOptions<
    { access_token: string; refresh_token: string; user: User },
    unknown,
    LoginRequest
  >
) {
  const queryClient = useQueryClient();
  const { setTokens, setUser } = useAuthStore();

  return useMutation({
    mutationFn: (credentials: LoginRequest) => authService.login(credentials),
    onSuccess: (data, variables, context) => {
      // Store tokens and user in auth store
      setTokens(data.access_token, data.refresh_token);
      setUser(data.user);
      
      // Clear all queries to fetch fresh data
      queryClient.clear();
      
      // Call the provided onSuccess callback
      options?.onSuccess?.(data, variables, context);
    },
    onError: (error, variables, context) => {
      console.error('Login error:', getErrorMessage(error));
      
      // Call the provided onError callback
      options?.onError?.(error, variables, context);
    },
    ...options,
  });
}

// Hook for signup
export function useSignup(
  options?: BaseMutationOptions<
    { access_token: string; refresh_token: string; user: User },
    unknown,
    SignupRequest
  >
) {
  const queryClient = useQueryClient();
  const { setTokens, setUser } = useAuthStore();

  return useMutation({
    mutationFn: (data: SignupRequest) => authService.signup(data),
    onSuccess: (data, variables, context) => {
      // Store tokens and user in auth store
      setTokens(data.access_token, data.refresh_token);
      setUser(data.user);
      
      // Clear all queries to fetch fresh data
      queryClient.clear();
      
      // Call the provided onSuccess callback
      options?.onSuccess?.(data, variables, context);
    },
    onError: (error, variables, context) => {
      console.error('Signup error:', getErrorMessage(error));
      
      // Call the provided onError callback
      options?.onError?.(error, variables, context);
    },
    ...options,
  });
}

// Hook for logout
export function useLogout(
  options?: BaseMutationOptions<void, unknown, void>
) {
  const queryClient = useQueryClient();
  const { logout: clearAuth } = useAuthStore();

  return useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: (data, variables, context) => {
      // Clear auth store
      clearAuth();
      
      // Clear all cached data
      queryClient.clear();
      
      // Call the provided onSuccess callback
      options?.onSuccess?.(data, variables, context);
    },
    onError: (error, variables, context) => {
      console.error('Logout error:', getErrorMessage(error));
      // Even if logout fails, clear local state
      clearAuth();
      queryClient.clear();
      
      // Call the provided onError callback
      options?.onError?.(error, variables, context);
    },
    ...options,
  });
}

// Hook for password reset request
export function useRequestPasswordReset(
  options?: BaseMutationOptions<{ message: string }, unknown, { email: string }>
) {
  return useMutation({
    mutationFn: ({ email }) => authService.requestPasswordReset(email),
    ...options,
  });
}

// Hook for password reset
export function useResetPassword(
  options?: BaseMutationOptions<{ message: string }, unknown, { token: string; password: string }>
) {
  return useMutation({
    mutationFn: ({ token, password }) => authService.resetPassword(token, password),
    ...options,
  });
}

// Hook for email verification
export function useVerifyEmail(
  options?: BaseMutationOptions<{ message: string }, unknown, string>
) {
  return useMutation({
    mutationFn: (token: string) => authService.verifyEmail(token),
    ...options,
  });
}

// Hook for refreshing token
export function useRefreshToken(
  options?: BaseMutationOptions<
    { access_token: string; refresh_token: string },
    unknown,
    void
  >
) {
  const { setTokens, refreshToken } = useAuthStore();

  return useMutation({
    mutationFn: () => {
      const token = refreshToken;
      if (!token) throw new Error('No refresh token available');
      return authService.refreshToken(token);
    },
    onSuccess: (data) => {
      // Update tokens in store
      setTokens(data.access_token, data.refresh_token);
    },
    ...options,
  });
}