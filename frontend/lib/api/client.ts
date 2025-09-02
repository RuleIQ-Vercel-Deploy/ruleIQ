import { useAuthStore } from '@/lib/stores/auth.store';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any,
  ) {
    super(message);
    this.name = 'APIError';
  }
}

class APIClient {
  private async getAuthHeaders(): Promise<HeadersInit> {
    const { tokens, refreshToken } = useAuthStore.getState();

    if (!tokens?.access_token) {
      throw new APIError('No authentication token available', 401);
    }

    // Check if token might be expired and try to refresh
    try {
      return {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${tokens.access_token}`,
      };
    } catch {
      // If we have a refresh token, try to refresh
      if (tokens.refresh_token) {
        try {
          await refreshToken();
          const newTokens = useAuthStore.getState().tokens;
          return {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${newTokens?.access_token}`,
          };
        } catch (refreshError) {
          throw new APIError('Authentication failed', 401);
        }
      }
      throw new APIError('Authentication failed', 401);
    }
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // Automatically prepend /api/v1 to endpoints unless they already start with /api
    const normalizedEndpoint = endpoint.startsWith('/api') ? endpoint : `/api/v1${endpoint}`;
    const url = `${API_BASE_URL}${normalizedEndpoint}`;

    try {
      const headers = await this.getAuthHeaders();

      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData,
        );
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return response.json();
      }

      return response.text() as unknown as T;
    } catch {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(error instanceof Error ? error.message : 'Network error', 0);
    }
  }

  private getPublicHeaders(): HeadersInit {
    return {
      'Content-Type': 'application/json',
    };
  }

  // Public request method for unauthenticated endpoints (like freemium)
  async publicRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // Automatically prepend /api/v1 to endpoints unless they already start with /api
    const normalizedEndpoint = endpoint.startsWith('/api') ? endpoint : `/api/v1${endpoint}`;
    const url = `${API_BASE_URL}${normalizedEndpoint}`;

    try {
      const headers = this.getPublicHeaders();

      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData,
        );
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return response.json();
      }

      return response.text() as unknown as T;
    } catch {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(error instanceof Error ? error.message : 'Network error', 0);
    }
  }

  // Convenience methods
  async get<T>(endpoint: string, options?: { params?: Record<string, any> }): Promise<T> {
    let url = endpoint;

    // Add query parameters if provided
    if (options?.params) {
      const searchParams = new URLSearchParams();
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += (endpoint.includes('?') ? '&' : '?') + queryString;
      }
    }

    return this.request<T>(url, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  async download(endpoint: string, filename: string): Promise<void> {
    const normalizedEndpoint = endpoint.startsWith('/api') ? endpoint : `/api/v1${endpoint}`;
    const url = `${API_BASE_URL}${normalizedEndpoint}`;

    try {
      const headers = await this.getAuthHeaders();

      const response = await fetch(url, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData,
        );
      }

      // Create download link
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(error instanceof Error ? error.message : 'Network error', 0);
    }
  }

  async upload<T>(endpoint: string, file: File, additionalData?: Record<string, any>): Promise<T> {
    const normalizedEndpoint = endpoint.startsWith('/api') ? endpoint : `/api/v1${endpoint}`;
    const url = `${API_BASE_URL}${normalizedEndpoint}`;

    try {
      const headers = await this.getAuthHeaders();
      // Remove Content-Type header to let browser set it with boundary for FormData
      delete (headers as any)['Content-Type'];

      const formData = new FormData();
      formData.append('file', file);

      // Add any additional data
      if (additionalData) {
        Object.entries(additionalData).forEach(([key, value]) => {
          formData.append(key, String(value));
        });
      }

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData,
        );
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return response.json();
      }

      return response.text() as unknown as T;
    } catch {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(error instanceof Error ? error.message : 'Network error', 0);
    }
  }

  // Public convenience methods for unauthenticated endpoints
  async publicGet<T>(endpoint: string, options?: { params?: Record<string, any> }): Promise<T> {
    let url = endpoint;

    // Add query parameters if provided
    if (options?.params) {
      const searchParams = new URLSearchParams();
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += (endpoint.includes('?') ? '&' : '?') + queryString;
      }
    }

    return this.publicRequest<T>(url, { method: 'GET' });
  }

  async publicPost<T>(endpoint: string, data?: any): Promise<T> {
    return this.publicRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
}

export const apiClient = new APIClient();
