import { describe, it, expect, beforeEach } from 'vitest'

// Mock data for testing
const mockUser = {
  id: '1',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  role: 'user',
  permissions: ['read', 'write'],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

const mockTokenResponse = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  token_type: 'bearer',
  expires_in: 3600
}

describe('Auth Store', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  it('should have initial state', async () => {
    // Import the store dynamically to avoid module loading issues
    const { useAuthStore } = await import('../../app/store/auth-store')
    const state = useAuthStore.getState()

    expect(state.accessToken).toBeNull()
    expect(state.refreshToken).toBeNull()
    expect(state.user).toBeNull()
    expect(state.isAuthenticated).toBe(false)
    expect(state.permissions).toEqual([])
    expect(state.role).toBeNull()
  })

  it('should login user successfully', async () => {
    const { useAuthStore } = await import('../../app/store/auth-store')
    const { login } = useAuthStore.getState()

    login(mockTokenResponse, mockUser)

    const state = useAuthStore.getState()
    expect(state.accessToken).toBe(mockTokenResponse.access_token)
    expect(state.refreshToken).toBe(mockTokenResponse.refresh_token)
    expect(state.user).toEqual(mockUser)
    expect(state.isAuthenticated).toBe(true)
    expect(state.permissions).toEqual(mockUser.permissions)
    expect(state.role).toBe(mockUser.role)
  })

  it('should logout user successfully', async () => {
    const { useAuthStore } = await import('../../app/store/auth-store')
    const { login, logout } = useAuthStore.getState()

    // First login
    login(mockTokenResponse, mockUser)
    expect(useAuthStore.getState().isAuthenticated).toBe(true)

    // Then logout
    logout()

    const state = useAuthStore.getState()
    expect(state.accessToken).toBeNull()
    expect(state.refreshToken).toBeNull()
    expect(state.user).toBeNull()
    expect(state.isAuthenticated).toBe(false)
    expect(state.permissions).toEqual([])
    expect(state.role).toBeNull()
  })

  it('should check permissions correctly', async () => {
    const { useAuthStore } = await import('../../app/store/auth-store')
    const { login, hasPermission, hasAnyPermission, hasAllPermissions } = useAuthStore.getState()

    const userWithPermissions = { ...mockUser, permissions: ['read', 'write', 'admin'] }
    login(mockTokenResponse, userWithPermissions)

    expect(hasPermission('read')).toBe(true)
    expect(hasPermission('delete')).toBe(false)
    expect(hasAnyPermission(['read', 'delete'])).toBe(true)
    expect(hasAnyPermission(['delete', 'super-admin'])).toBe(false)
    expect(hasAllPermissions(['read', 'write'])).toBe(true)
    expect(hasAllPermissions(['read', 'delete'])).toBe(false)
  })
})
