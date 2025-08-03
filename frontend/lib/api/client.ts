import { useAuthStore } from '@/lib/stores/auth.store';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
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
        'Authorization': `Bearer ${tokens.access_token}`,
      };
    } catch (error) {
      // If we have a refresh token, try to refresh
      if (tokens.refresh_token) {
        try {
          await refreshToken();
          const newTokens = useAuthStore.getState().tokens;
          return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${newTokens?.access_token}`,
          };
        } catch (refreshError) {
          throw new APIError('Authentication failed', 401);
        }
      }
      throw new APIError('Authentication failed', 401);
    }
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
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
          errorData
        );
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return response.json();
      }
      
      return response.text() as unknown as T;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(
        error instanceof Error ? error.message : 'Network error',
        0
      );
    }
  }

  

  // Convenience methods
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
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
}

export const apiClient = new APIClient();