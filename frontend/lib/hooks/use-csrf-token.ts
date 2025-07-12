import { useState, useEffect } from 'react';

interface CsrfTokenResponse {
  csrfToken: string;
  message: string;
}

/**
 * Hook to fetch and manage CSRF tokens
 */
export function useCsrfToken() {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchToken = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/csrf-token', {
        method: 'GET',
        credentials: 'include', // Include cookies
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch CSRF token: ${response.statusText}`);
      }
      
      const data: CsrfTokenResponse = await response.json();
      setToken(data.csrfToken);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('CSRF token fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchToken();
  }, []);

  return {
    token,
    loading,
    error,
    refetch: fetchToken,
  };
}

/**
 * Get CSRF token headers for API requests
 */
export function getCsrfHeaders(token: string) {
  return {
    'X-CSRF-Token': token,
    'Content-Type': 'application/json',
  };
}

/**
 * Create form data with CSRF token
 */
export function createCsrfFormData(token: string, data: Record<string, any>) {
  const formData = new FormData();
  formData.append('_csrf', token);
  
  Object.entries(data).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      formData.append(key, value);
    }
  });
  
  return formData;
}