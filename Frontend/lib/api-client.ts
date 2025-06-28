// Enterprise API Client for NexCompli
import { z } from 'zod';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Response types
interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

class ApiClient {
  private baseURL: string;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
    // Initialize tokens from localStorage if available
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    if (this.accessToken) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${this.accessToken}`,
      };
    }

    try {
      const response = await fetch(url, config);
      
      // Handle 401 - attempt token refresh
      if (response.status === 401 && this.refreshToken && endpoint !== '/api/auth/refresh') {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry original request with new token
          config.headers = {
            ...config.headers,
            Authorization: `Bearer ${this.accessToken}`,
          };
          return this.request(endpoint, options);
        } else {
          // Refresh failed, redirect to login
          this.clearTokens();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          throw new Error('Authentication failed');
        }
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  private async refreshAccessToken(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.refreshToken}`,
        },
      });

      if (response.ok) {
        const tokens: AuthTokens = await response.json();
        this.setTokens(tokens);
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }
    return false;
  }

  private setTokens(tokens: AuthTokens) {
    this.accessToken = tokens.access_token;
    this.refreshToken = tokens.refresh_token;
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
    }
  }

  private clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<AuthTokens> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseURL}/api/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Login failed');
    }

    const tokens: AuthTokens = await response.json();
    this.setTokens(tokens);
    return tokens;
  }

  async register(email: string, password: string): Promise<ApiResponse> {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async logout(): Promise<void> {
    try {
      await this.request('/api/auth/logout', { method: 'POST' });
    } finally {
      this.clearTokens();
    }
  }

  // User endpoints
  async getUserProfile(): Promise<any> {
    return this.request('/api/users/profile');
  }

  // Business profile endpoints
  async getBusinessProfiles(): Promise<any[]> {
    return this.request('/api/business-profiles');
  }

  async getBusinessProfile(id: string): Promise<any> {
    return this.request(`/api/business-profiles/${id}`);
  }

  async createBusinessProfile(data: any): Promise<any> {
    return this.request('/api/business-profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateBusinessProfile(id: string, data: any): Promise<any> {
    return this.request(`/api/business-profiles/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Assessment endpoints
  async createAssessment(data: any): Promise<any> {
    return this.request('/api/assessments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getAssessment(id: string): Promise<any> {
    return this.request(`/api/assessments/${id}`);
  }

  async updateAssessment(id: string, data: any): Promise<any> {
    return this.request(`/api/assessments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Framework endpoints
  async getFrameworks(): Promise<any[]> {
    return this.request('/api/frameworks');
  }

  async getFrameworkRecommendations(businessProfileId: string): Promise<any[]> {
    return this.request(`/api/frameworks/recommendations/${businessProfileId}`);
  }

  // Evidence endpoints
  async getEvidence(params?: Record<string, any>): Promise<any> {
    const searchParams = params ? `?${new URLSearchParams(params)}` : '';
    return this.request(`/api/evidence${searchParams}`);
  }

  async createEvidence(data: any): Promise<any> {
    return this.request('/api/evidence', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateEvidence(id: string, data: any): Promise<any> {
    return this.request(`/api/evidence/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteEvidence(id: string): Promise<void> {
    return this.request(`/api/evidence/${id}`, { method: 'DELETE' });
  }

  async searchEvidence(query: string): Promise<any[]> {
    return this.request(`/api/evidence/search?q=${encodeURIComponent(query)}`);
  }

  // Chat endpoints
  async getChatConversations(): Promise<any[]> {
    return this.request('/api/chat/conversations');
  }

  async createChatConversation(): Promise<any> {
    return this.request('/api/chat/conversations', { method: 'POST' });
  }

  async getChatMessages(conversationId: string): Promise<any[]> {
    return this.request(`/api/chat/conversations/${conversationId}`);
  }

  async sendChatMessage(conversationId: string, message: string): Promise<any> {
    return this.request(`/api/chat/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // Report endpoints
  async generateReport(data: any): Promise<any> {
    return this.request('/api/reports/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getReportHistory(): Promise<any[]> {
    return this.request('/api/reports/history');
  }

  // Readiness endpoints
  async getReadinessScore(businessProfileId: string): Promise<any> {
    return this.request(`/api/readiness/${businessProfileId}`);
  }

  async getGapAnalysis(businessProfileId: string): Promise<any> {
    return this.request(`/api/readiness/gaps/${businessProfileId}`);
  }

  // Integration endpoints
  async getIntegrations(): Promise<any[]> {
    return this.request('/api/integrations');
  }

  async connectIntegration(provider: string): Promise<any> {
    return this.request('/api/integrations/connect', {
      method: 'POST',
      body: JSON.stringify({ provider }),
    });
  }

  // Monitoring endpoints (admin)
  async getDatabaseStatus(): Promise<any> {
    return this.request('/api/monitoring/database/status');
  }

  async getSystemAlerts(): Promise<any[]> {
    return this.request('/api/monitoring/alerts');
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }
}

export const apiClient = new ApiClient();
export default apiClient;