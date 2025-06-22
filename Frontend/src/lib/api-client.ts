import axios, { type AxiosError } from "axios"
import { retryRequest } from "./retry-mechanism"

// Get API configuration from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || "30000")

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json",
  },
  withCredentials: false, // Set to true if using cookies for auth
})

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage using environment variable key
    const tokenKey = process.env.NEXT_PUBLIC_AUTH_TOKEN_KEY || "nexcompli_auth_token"
    const token = localStorage.getItem(tokenKey)

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Add request ID for debugging
    config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor for error handling with retry
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    // Handle token expiration
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // Clear tokens using environment variable keys
      const tokenKey = process.env.NEXT_PUBLIC_AUTH_TOKEN_KEY || "nexcompli_auth_token"
      const refreshKey = process.env.NEXT_PUBLIC_AUTH_REFRESH_KEY || "nexcompli_refresh_token"
      const userKey = process.env.NEXT_PUBLIC_AUTH_USER_KEY || "nexcompli_user"

      localStorage.removeItem(tokenKey)
      localStorage.removeItem(refreshKey)
      localStorage.removeItem(userKey)

      // Redirect to login page
      window.location.href = "/login"
      return Promise.reject(error)
    }

    // Retry logic for network errors and 5xx errors
    if (
      !originalRequest._retry &&
      (error.code === "NETWORK_ERROR" || (error.response?.status && error.response.status >= 500))
    ) {
      return retryRequest(() => apiClient(originalRequest), {
        maxAttempts: 3,
        delay: 1000,
        backoff: "exponential",
      })
    }

    return Promise.reject(error)
  },
)

export default apiClient
