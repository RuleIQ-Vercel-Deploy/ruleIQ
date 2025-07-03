import axios, { type AxiosInstance, type AxiosRequestConfig, AxiosResponse, type AxiosError } from 'axios';

import { API_TIMEOUT, API_RETRY_ATTEMPTS, API_RETRY_DELAY, AUTH_TOKEN_KEY, REFRESH_TOKEN_KEY } from '@/config/constants';
import { env } from '@/config/env';

import { handleApiError, retryWithBackoff, ErrorType, logError } from './error-handler';

import type { ApiResponse, ApiError as ApiErrorType } from '@/types/global';


/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public originalError?: AxiosError
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

/**
 * API client configuration
 */
class ApiClient {
  private client: AxiosInstance;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: env.NEXT_PUBLIC_API_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * Setup request and response interceptors
   */
  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            await this.refreshAccessToken();
            const token = this.getAccessToken();
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            this.clearTokens();
            window.location.href = '/auth/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(this.handleError(error));
      }
    );
  }

  /**
   * Handle API errors with enhanced error handling
   */
  private handleError(error: AxiosError<ApiErrorType>): ApiError {
    try {
      const enhancedError = handleApiError(error);

      // Ensure we have a valid error object before logging
      if (enhancedError) {
        logError(enhancedError, {
          endpoint: error.config?.url,
          method: error.config?.method,
        });

        // Return ApiError for backward compatibility
        return new ApiError(
          enhancedError.status || 500,
          enhancedError.userMessage || 'An unexpected error occurred',
          error
        );
      }
    } catch (handlingError) {
      console.error('[ruleIQ] Error in error handling:', handlingError);
    }

    // Fallback error handling
    return new ApiError(
      error.response?.status || 500,
      'An unexpected error occurred',
      error
    );
  }

  /**
   * Get access token from storage
   */
  private getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(AUTH_TOKEN_KEY);
  }

  /**
   * Get refresh token from storage
   */
  private getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  /**
   * Store tokens
   */
  private setTokens(accessToken: string, refreshToken: string) {
    if (typeof window === 'undefined') return;
    localStorage.setItem(AUTH_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }

  /**
   * Clear tokens
   */
  private clearTokens() {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  /**
   * Refresh access token
   */
  private async refreshAccessToken(): Promise<string> {
    // Prevent multiple refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    this.refreshPromise = this.post<{ access_token: string; refresh_token: string }>(
      '/auth/refresh',
      { refresh_token: refreshToken },
      { _skipAuthRefresh: true } as any
    ).then((response) => {
      const { access_token, refresh_token } = response.data;
      this.setTokens(access_token, refresh_token);
      this.refreshPromise = null;
      return access_token;
    }).catch((error) => {
      this.refreshPromise = null;
      throw error;
    });

    return this.refreshPromise;
  }

  /**
   * Enhanced retry with exponential backoff
   */
  private async retryRequest<T>(
    fn: () => Promise<T>,
    context?: string
  ): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      const axiosError = (error as ApiError).originalError;
      if (axiosError) {
        const enhancedError = handleApiError(axiosError);
        
        if (enhancedError.retryable) {
          return retryWithBackoff(
            fn,
            enhancedError.type,
            (attempt, delay) => {
              console.log(`Retrying request (attempt ${attempt}) after ${delay}ms delay`);
            }
          );
        }
      }
      throw error;
    }
  }

  /**
   * GET request
   */
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.retryRequest(async () => {
      const response = await this.client.get<ApiResponse<T>>(url, config);
      return response.data;
    });
  }

  /**
   * POST request
   */
  async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.retryRequest(async () => {
      const response = await this.client.post<ApiResponse<T>>(url, data, config);
      return response.data;
    });
  }

  /**
   * PUT request
   */
  async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.retryRequest(async () => {
      const response = await this.client.put<ApiResponse<T>>(url, data, config);
      return response.data;
    });
  }

  /**
   * PATCH request
   */
  async patch<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.retryRequest(async () => {
      const response = await this.client.patch<ApiResponse<T>>(url, data, config);
      return response.data;
    });
  }

  /**
   * DELETE request
   */
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.retryRequest(async () => {
      const response = await this.client.delete<ApiResponse<T>>(url, config);
      return response.data;
    });
  }

  /**
   * Upload file
   */
  async upload<T = any>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
  }

  /**
   * Download file
   */
  async download(url: string, filename?: string): Promise<void> {
    const response = await this.client.get(url, {
      responseType: 'blob',
    });

    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();