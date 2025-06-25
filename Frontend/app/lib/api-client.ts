import axios, { type AxiosError } from "axios"

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
  withCredentials: false,
})

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage (only on client side)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem("access_token")
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }

    // Add request ID for debugging
    config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    // Handle token expiration
    if (error.response?.status === 401 && !originalRequest._retry && typeof window !== 'undefined') {
      originalRequest._retry = true

      // Clear tokens
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")

      // Redirect to login page
      window.location.href = "/login"
      return Promise.reject(error)
    }

    return Promise.reject(error)
  },
)

export default apiClient