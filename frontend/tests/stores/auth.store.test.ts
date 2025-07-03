import { describe, it, expect, beforeEach, vi } from 'vitest'

import { useAuthStore } from '@/lib/stores/auth.store'

// Mock the auth service
vi.mock('@/lib/api/auth.service', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    refreshToken: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}))

describe('Auth Store', () => {
  beforeEach(async () => {
    // Reset store state before each test
    await useAuthStore.getState().logout()
    vi.clearAllMocks()
  })

  it('has correct initial state', () => {
    const state = useAuthStore.getState()

    expect(state.user).toBeNull()
    expect(state.tokens.access).toBeNull()
    expect(state.tokens.refresh).toBeNull()
    expect(state.isAuthenticated).toBe(false)
    expect(state.isLoading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('sets loading state correctly', () => {
    const { setLoading } = useAuthStore.getState()
    
    setLoading(true)
    expect(useAuthStore.getState().isLoading).toBe(true)
    
    setLoading(false)
    expect(useAuthStore.getState().isLoading).toBe(false)
  })

  it('sets error state correctly', () => {
    const { setError, clearError } = useAuthStore.getState()
    
    setError('Test error')
    expect(useAuthStore.getState().error).toBe('Test error')
    
    clearError()
    expect(useAuthStore.getState().error).toBeNull()
  })

  it('sets user on login success', () => {
    const { setUser } = useAuthStore.getState()

    const mockUser = {
      id: '1',
      email: 'test@example.com',
      created_at: new Date().toISOString(),
      is_active: true,
    }

    setUser(mockUser)

    const state = useAuthStore.getState()
    expect(state.user).toEqual(mockUser)
  })

  it('clears state on logout', async () => {
    const { setUser, logout } = useAuthStore.getState()

    // Set some state first
    setUser({
      id: '1',
      email: 'test@example.com',
      created_at: new Date().toISOString(),
      is_active: true,
    })

    // Logout
    await logout()

    // Verify state is cleared
    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.tokens.access).toBeNull()
    expect(state.tokens.refresh).toBeNull()
    expect(state.isAuthenticated).toBe(false)
    expect(state.error).toBeNull()
  })

  it('updates user profile correctly', () => {
    const { setUser } = useAuthStore.getState()

    const initialUser = {
      id: '1',
      email: 'test@example.com',
      created_at: new Date().toISOString(),
      is_active: true,
    }

    setUser(initialUser)

    const updatedUser = {
      ...initialUser,
      email: 'updated@example.com',
    }

    setUser(updatedUser)

    expect(useAuthStore.getState().user).toEqual(updatedUser)
  })
})
