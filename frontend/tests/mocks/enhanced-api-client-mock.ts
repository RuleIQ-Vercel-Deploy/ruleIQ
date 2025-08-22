import { vi } from 'vitest';

// Enhanced API client mock with proper error handling
export const createEnhancedApiClient = () => {
  const mockClient = {
    get: vi.fn().mockImplementation((url, options = {}) => {
    // TODO: Replace with proper logging
      // Handle specific endpoints with proper responses
      if (url.includes('/auth/me')) {
        return Promise.resolve({
          data: {
            id: 'user-123',
            email: 'test@example.com',
            name: 'Test User',
            is_active: true
          }
        });
      }
      
      if (url.includes('/business-profiles')) {
        return Promise.resolve({
          data: {
            items: [
              { id: 'profile-1', company_name: 'Test Company' }
            ],
            total: 1,
            page: 1,
            size: 20
          }
        });
      }
      
      if (url.includes('/assessments')) {
        // Handle specific assessment ID requests
        if (url.includes('assess-123')) {
          return Promise.resolve({
            data: {
              id: 'assess-123',
              name: 'Test Assessment',
              status: 'completed'
            }
          });
        }
        
        return Promise.resolve({
          data: {
            items: [
              { id: 'assess-1', name: 'Test Assessment 1' },
              { id: 'assess-2', name: 'Test Assessment 2' }
            ],
            total: 2,
            page: 1,
            size: 20
          }
        });
      }
      
      if (url.includes('/evidence')) {
        return Promise.resolve({
          data: {
            items: [
              { id: 'evidence-1', name: 'Test Evidence', status: 'approved' }
            ],
            total: 1,
            page: 1,
            size: 20
          }
        });
      }
      
      // Default response with data wrapper
      return Promise.resolve({
        data: { success: true }
      });
    }),
    
    post: vi.fn().mockImplementation((url, data, options = {}) => {
    // TODO: Replace with proper logging
      if (url.includes('/auth/login')) {
        // Handle invalid credentials
        if (data.email === 'invalid@example.com') {
          return Promise.reject(new Error('Invalid credentials'));
        }
        
        return Promise.resolve({
          data: {
            tokens: {
              access_token: 'mock-access-token',
              refresh_token: 'mock-refresh-token'
            },
            user: {
              id: 'user-123',
              email: 'test@example.com',
              name: 'Test User',
              is_active: true
            }
          }
        });
      }
      
      if (url.includes('/auth/register')) {
        // Handle validation errors
        if (data.password && data.password.length < 8) {
          return Promise.reject(new Error('Password must be at least 8 characters'));
        }
        
        return Promise.resolve({
          data: {
            tokens: {
              access_token: 'new-access-token',
              refresh_token: 'new-refresh-token'
            },
            user: {
              id: 'user-456',
              email: 'newuser@example.com',
              name: 'New User',
              is_active: true
            }
          }
        });
      }
      
      if (url.includes('/assessments')) {
        return Promise.resolve({
          data: {
            id: 'assess-new',
            name: 'New Assessment',
            status: 'draft',
            framework_id: 'gdpr',
            business_profile_id: 'profile-123'
          }
        });
      }
      
      if (url.includes('/evidence')) {
        return Promise.resolve({
          data: {
            id: 'evidence-new',
            title: 'Test Evidence',
            status: 'pending'
          }
        });
      }
      
      // Default response
      return Promise.resolve({
        data: { success: true, id: 'new-item' }
      });
    }),
    
    put: vi.fn().mockImplementation((url, data, options = {}) => {
    // TODO: Replace with proper logging
      // Handle specific assessment updates
      if (url.includes('assess-123')) {
        return Promise.resolve({
          data: {
            id: 'assess-123',
            status: 'completed',
            ...data
          }
        });
      }
      
      return Promise.resolve({
        data: { success: true, ...data }
      });
    }),
    
    patch: vi.fn().mockImplementation((url, data, options = {}) => {
    // TODO: Replace with proper logging
      return Promise.resolve({
        data: { success: true, ...data }
      });
    }),
    
    delete: vi.fn().mockImplementation((url, options = {}) => {
    // TODO: Replace with proper logging
      return Promise.resolve({
        data: { success: true }
      });
    }),
    
    request: vi.fn().mockImplementation((method, url, options = {}) => {
    // TODO: Replace with proper logging
      const client = createEnhancedApiClient();
      switch (method.toLowerCase()) {
        case 'get':
          return client.get(url, options);
        case 'post':
          return client.post(url, options.data, options);
        case 'put':
          return client.put(url, options.data, options);
        case 'patch':
          return client.patch(url, options.data, options);
        case 'delete':
          return client.delete(url, options);
        default:
          return Promise.resolve({ data: { success: true } });
      }
    })
  };
  
  return mockClient;
};

// Global enhanced API client
export const enhancedApiClient = createEnhancedApiClient();
