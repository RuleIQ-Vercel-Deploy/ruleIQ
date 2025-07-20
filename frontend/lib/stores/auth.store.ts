"use client"

import { create } from 'zustand'
import { persist, createJSONStorage , devtools } from 'zustand/middleware'

import SecureStorage from '@/lib/utils/secure-storage'

import type { User } from '@/types/api'

// Enhanced User interface for auth
export interface AuthUser extends User {
  firstName?: string
  lastName?: string
  companyId?: string
  lastLogin?: string
  emailVerified?: boolean
  businessProfile?: {
    id: string
    company_name: string
    industry: string
  }
}

// Login form data interface
export interface LoginFormData {
  email: string
  password: string
  rememberMe: boolean
}

// Registration form data interface
export interface RegistrationData {
  // Step 1: Account credentials
  email: string
  password: string
  confirmPassword: string

  // Step 2: Personal & company info
  firstName: string
  lastName: string
  companyName: string
  companySize: 'micro' | 'small' | 'medium' | 'large'
  industry: string

  // Step 3: Compliance needs
  complianceFrameworks: string[]
  hasDataProtectionOfficer: boolean
  agreedToTerms: boolean
  agreedToDataProcessing: boolean
}

interface AuthState {
  // State
  user: AuthUser | null
  tokens: {
    access: string | null
    refresh: string | null
  }
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  sessionExpiry: number | null

  // Legacy support
  accessToken: string | null
  refreshToken: string | null
  permissions: string[]
  role: string | null

  // Actions
  login: (credentials: LoginFormData) => Promise<void>
  register: (data: RegistrationData) => Promise<void>
  logout: () => Promise<void>
  refreshTokens: () => Promise<void>
  clearError: () => void
  checkAuth: () => Promise<void>
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // Legacy actions
  setUser: (user: User) => void
  updatePermissions: (permissions: string[]) => void
  hasPermission: (permission: string) => boolean
  hasRole: (role: string) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
  hasAllPermissions: (permissions: string[]) => boolean
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        // State initialization
        user: process.env.NODE_ENV === 'development' && process.env['NEXT_PUBLIC_ENABLE_MOCK_DATA'] === 'true' ? {
          id: 'demo-user',
          email: 'demo@ruleiq.com',
          created_at: new Date().toISOString(),
          is_active: true,
          firstName: 'Demo',
          lastName: 'User',
          companyId: 'demo-company',
          lastLogin: new Date().toISOString(),
          emailVerified: true,
          role: 'admin',
          permissions: ['read', 'write', 'admin']
        } : null,
        tokens: {
          access: process.env.NODE_ENV === 'development' && process.env['NEXT_PUBLIC_ENABLE_MOCK_DATA'] === 'true' ? 'demo-token' : null,
          refresh: process.env.NODE_ENV === 'development' && process.env['NEXT_PUBLIC_ENABLE_MOCK_DATA'] === 'true' ? 'demo-refresh' : null,
        },
        isAuthenticated: process.env.NODE_ENV === 'development' && process.env['NEXT_PUBLIC_ENABLE_MOCK_DATA'] === 'true',
        isLoading: false,
        error: null,
        sessionExpiry: null,

        // Legacy support
        accessToken: null,
        refreshToken: null,
        permissions: [],
        role: null,

        // Enhanced login action
        login: async (credentials: LoginFormData) => {
          set({ isLoading: true, error: null }, false, 'login/start')

          try {
            // Import auth service dynamically to avoid circular dependencies
            const { authService } = await import('@/lib/api/auth.service')
            const response = await authService.login(credentials)

            const { tokens, user } = response
            const expiryTime = Date.now() + (8 * 60 * 60 * 1000) // 8 hours

            // Store tokens securely using Web Crypto API
            if (typeof window !== 'undefined') {
              await SecureStorage.setAccessToken(tokens.access_token, {
                expiry: expiryTime
              })
              SecureStorage.setRefreshToken(tokens.refresh_token, expiryTime)
            }

            set({
              user: user as AuthUser,
              tokens: {
                access: tokens.access_token,
                refresh: tokens.refresh_token,
              },
              isAuthenticated: true,
              sessionExpiry: expiryTime,
              isLoading: false,
              error: null,
              // Legacy support
              accessToken: tokens.access_token,
              refreshToken: tokens.refresh_token,
              permissions: user.permissions || [],
              role: user.role || null,
            }, false, 'login/success')
          } catch (error: any) {
            set({
              isLoading: false,
              error: error.detail || error.message || 'Login failed. Please try again.',
            }, false, 'login/error')
            throw error
          }
        },

        // Enhanced register action
        register: async (data: RegistrationData) => {
          set({ isLoading: true, error: null }, false, 'register/start')

          try {
            const { authService } = await import('@/lib/api/auth.service')
            
            // Map registration data to API format
            const apiData = {
              email: data.email,
              password: data.password,
              name: `${data.firstName} ${data.lastName}`,
              company_name: data.companyName,
              company_size: data.companySize,
              industry: data.industry,
              compliance_frameworks: data.complianceFrameworks,
              has_dpo: data.hasDataProtectionOfficer,
              agreed_to_terms: data.agreedToTerms,
              agreed_to_data_processing: data.agreedToDataProcessing,
            }
            
            const response = await authService.register(apiData)

            const { tokens, user } = response
            const expiryTime = Date.now() + (8 * 60 * 60 * 1000) // 8 hours

            // Store tokens securely using Web Crypto API
            if (typeof window !== 'undefined') {
              await SecureStorage.setAccessToken(tokens.access_token, {
                expiry: expiryTime
              })
              SecureStorage.setRefreshToken(tokens.refresh_token, expiryTime)
            }

            set({
              user: user as AuthUser,
              tokens: {
                access: tokens.access_token,
                refresh: tokens.refresh_token,
              },
              isAuthenticated: true,
              sessionExpiry: expiryTime,
              isLoading: false,
              error: null,
              // Legacy support
              accessToken: tokens.access_token,
              refreshToken: tokens.refresh_token,
              permissions: user.permissions || [],
              role: user.role || null,
            }, false, 'register/success')
          } catch (error: any) {
            set({
              isLoading: false,
              error: error.detail || error.message || 'Registration failed. Please try again.',
            }, false, 'register/error')
            throw error
          }
        },

        // Enhanced logout action
        logout: async () => {
          set({ isLoading: true }, false, 'logout/start')

          try {
            const { authService } = await import('@/lib/api/auth.service')
            await authService.logout()
          } catch (error) {
            // Continue with logout even if API call fails
            console.error('Logout API call failed:', error)
          }

          // Clear all secure storage
          if (typeof window !== 'undefined') {
            SecureStorage.clearAll()
          }

          set({
            user: null,
            tokens: {
              access: null,
              refresh: null,
            },
            isAuthenticated: false,
            isLoading: false,
            error: null,
            sessionExpiry: null,
            // Legacy support
            accessToken: null,
            refreshToken: null,
            permissions: [],
            role: null,
          }, false, 'logout/complete')
        },

        // Token refresh action
        refreshTokens: async () => {
          let refreshToken: string | null = null
          
          if (typeof window !== 'undefined') {
            refreshToken = SecureStorage.getRefreshToken()
          }
          
          if (!refreshToken) {
            throw new Error('No refresh token available')
          }

          try {
            const { authService } = await import('@/lib/api/auth.service')
            const formData = new FormData()
            formData.append('refresh_token', refreshToken)
            
            const response = await authService.post('/auth/refresh', formData)

            const expiryTime = Date.now() + (8 * 60 * 60 * 1000) // 8 hours

            // Update stored tokens securely
            if (typeof window !== 'undefined') {
              await SecureStorage.setAccessToken(response.data.access_token, {
                expiry: expiryTime
              })
              SecureStorage.setRefreshToken(response.data.refresh_token, expiryTime)
            }

            set({
              tokens: {
                access: response.data.access_token,
                refresh: response.data.refresh_token,
              },
              sessionExpiry: expiryTime,
              // Legacy support
              accessToken: response.data.access_token,
              refreshToken: response.data.refresh_token,
            }, false, 'refreshTokens')
          } catch (error) {
            // If refresh fails, logout user
            get().logout()
            throw error
          }
        },

        // Check authentication status
        checkAuth: async () => {
          set({ isLoading: true }, false, 'checkAuth/start')

          try {
            // Migrate legacy tokens if they exist
            if (typeof window !== 'undefined') {
              await SecureStorage.migrateLegacyTokens()
            }

            // Check for stored tokens using secure storage
            let accessToken: string | null = null
            let refreshToken: string | null = null
            let sessionExpiry: number | null = null

            if (typeof window !== 'undefined') {
              accessToken = await SecureStorage.getAccessToken()
              refreshToken = SecureStorage.getRefreshToken()
              sessionExpiry = SecureStorage.getSessionExpiry()
            }

            if (!accessToken || !refreshToken) {
              set({ isLoading: false }, false, 'checkAuth/noTokens')
              return
            }

            // Check if session is expired
            if (SecureStorage.isSessionExpired()) {
              get().logout()
              return
            }

            // Verify token with backend
            const { authService } = await import('@/lib/api/auth.service')
            const user = await authService.getCurrentUser()

            set({
              user: user as AuthUser,
              tokens: {
                access: accessToken,
                refresh: refreshToken,
              },
              isAuthenticated: true,
              sessionExpiry,
              isLoading: false,
              error: null,
              // Legacy support
              accessToken,
              refreshToken,
              permissions: user.permissions || [],
              role: user.role || null,
            }, false, 'checkAuth/success')
          } catch (error) {
            // If verification fails, clear auth state
            get().logout()
          }
        },

        // Utility actions
        clearError: () => set({ error: null }, false, 'clearError'),
        setLoading: (loading: boolean) => set({ isLoading: loading }, false, 'setLoading'),
        setError: (error: string | null) => set({ error }, false, 'setError'),

        // Legacy methods
        setUser: (user) =>
          set({
            user: user as AuthUser,
            permissions: user.permissions || [],
            role: user.role || null,
          }, false, 'setUser'),

        updatePermissions: (permissions) => set({ permissions }, false, 'updatePermissions'),

        hasPermission: (permission) => {
          const { permissions } = get()
          return permissions.includes(permission)
        },

        hasRole: (role) => {
          const { role: userRole } = get()
          return userRole === role
        },

        hasAnyPermission: (permissions) => {
          const { permissions: userPermissions } = get()
          return permissions.some((permission) => userPermissions.includes(permission))
        },

        hasAllPermissions: (permissions) => {
          const { permissions: userPermissions } = get()
          return permissions.every((permission) => userPermissions.includes(permission))
        },
      }),
      {
        name: "ruleiq-auth-storage",
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          // Only persist essential data, tokens are stored separately
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          sessionExpiry: state.sessionExpiry,
          // Legacy support
          permissions: state.permissions,
          role: state.role,
        }),
        skipHydration: true,
      },
    ),
    {
      name: 'auth-store'
    }
  )
)

// Selectors
export const selectUser = (state: AuthState) => state.user
export const selectIsAuthenticated = (state: AuthState) => state.isAuthenticated
export const selectAuthLoading = (state: AuthState) => state.isLoading
export const selectAuthError = (state: AuthState) => state.error
export const selectPermissions = (state: AuthState) => state.permissions
export const selectRole = (state: AuthState) => state.role