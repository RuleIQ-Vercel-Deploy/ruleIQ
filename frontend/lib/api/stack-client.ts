import { stackServerApp } from '@/app/stack';

export class StackAPIClient {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async authenticatedFetch(endpoint: string, options: RequestInit = {}) {
    const user = await stackServerApp.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }

    // Get the access token from Stack Auth
    const tokens = await user.getAuthJson();
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${tokens.accessToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  }

  // Dashboard API
  async getDashboardData() {
    return this.authenticatedFetch('/api/dashboard');
  }

  // Business Profiles API
  async getBusinessProfiles() {
    return this.authenticatedFetch('/api/business-profiles');
  }

  async createBusinessProfile(data: any) {
    return this.authenticatedFetch('/api/business-profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Assessments API
  async getAssessments() {
    return this.authenticatedFetch('/api/assessments');
  }

  // Policies API
  async getPolicies() {
    return this.authenticatedFetch('/api/policies');
  }
}

export const stackAPIClient = new StackAPIClient();
