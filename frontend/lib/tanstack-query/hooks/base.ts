import { type UseQueryOptions, type UseMutationOptions } from '@tanstack/react-query';
import { AxiosError } from 'axios';

// Common error type for API responses
export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
  errors?: Record<string, string[]>;
}

// Helper to extract error message
export const getErrorMessage = (error: unknown): string => {
  // Handle AxiosError
  if (error instanceof AxiosError) {
    const responseError = error.response?.data;
    
    // Check for various error message formats
    if (responseError) {
      // API error formats
      if (typeof responseError.detail === 'string') return responseError.detail;
      if (typeof responseError.message === 'string') return responseError.message;
      if (typeof responseError.error === 'string') return responseError.error;
      
      // Handle validation errors
      if (responseError.errors && typeof responseError.errors === 'object') {
        const firstError = Object.values(responseError.errors).flat()[0];
        if (typeof firstError === 'string') return firstError;
      }
    }
    
    // Network errors
    if (error.code === 'ECONNABORTED') return 'Request timeout';
    if (error.code === 'ERR_NETWORK') return 'Network error - please check your connection';
    if (!error.response) return 'Network error - server unreachable';
    
    return error.message || 'An unexpected error occurred';
  }
  
  // Handle regular Error instances
  if (error instanceof Error) {
    return error.message;
  }
  
  // Handle string errors
  if (typeof error === 'string') {
    return error;
  }
  
  // Handle objects with message property
  if (error && typeof error === 'object' && 'message' in error) {
    return String(error.message);
  }
  
  return 'An unexpected error occurred';
};

// Base query options with proper typing
export type BaseQueryOptions<TData, TError = ApiError> = Omit<
  UseQueryOptions<TData, TError>,
  'queryKey' | 'queryFn'
>;

// Base mutation options with proper typing
export type BaseMutationOptions<TData, TError = ApiError, TVariables = void> = Omit<
  UseMutationOptions<TData, TError, TVariables>,
  'mutationFn'
>;

// Helper to create query keys with proper structure
export const createQueryKey = (
  domain: string,
  action: string,
  params?: Record<string, any>
): string[] => {
  const key = [domain, action];
  if (params) {
    key.push(JSON.stringify(params));
  }
  return key;
};

// Helper for pagination params
export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort?: string;
  order?: 'asc' | 'desc';
}

// Common response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}