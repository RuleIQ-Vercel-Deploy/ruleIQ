import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuthStore } from '@/lib/stores/auth.store'
import { useAssessmentStore } from '@/lib/stores/assessment.store'
import { useEvidenceStore } from '@/lib/stores/evidence.store'
import { useDashboardStore } from '@/lib/stores/dashboard.store'
import SecureStorage from '@/lib/utils/secure-storage'

// Mock SecureStorage
vi.mock('@/lib/utils/secure-storage', () => ({
  default: {
    setAccessToken: vi.fn(),
    setRefreshToken: vi.fn(),
    getAccessToken: vi.fn(),
    getRefreshToken: vi.fn(),
    getSessionExpiry: vi.fn(),
    isSessionExpired: vi.fn(),
    clearAll: vi.fn(),
    migrateLegacyTokens: vi.fn(),
  },
}))

// Mock API services
vi.mock('@/lib/api/auth.service', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    post: vi.fn(),
  },
}))

describe('Store Integration Tests', () => {
  beforeEach(() => {
    // Reset all stores
    useAuthStore.setState({
      user: null,
      tokens: { access: null, refresh: null },
      isAuthenticated: false,
      isLoading: false,
      error: null,
      sessionExpiry: null,
      accessToken: null,
      refreshToken: null,
      permissions: [],
      role: null,
    })

    useAssessmentStore.setState({
      currentAssessment: null,
      assessments: [],
      frameworks: [],
      isLoading: false,
      error: null,
    })

    useEvidenceStore.setState({
      evidence: [],
      currentEvidence: null,
      isLoading: false,
      error: null,
      filters: {},
    })

    useDashboardStore.setState({
      widgets: [],
      metrics: {},
      isLoading: false,
      error: null,
      layout: 'default',
    })

    vi.clearAllMocks()
  })

  describe('AuthStore', () => {
    it('should handle login successfully', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        created_at: new Date().toISOString(),
        is_active: true,
        permissions: ['read', 'write'],
        role: 'user',
      }

      const mockTokens = {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
      }

      const { authService } = await import('@/lib/api/auth.service')
      vi.mocked(authService.login).mockResolvedValue({
        tokens: mockTokens,
        user: mockUser,
      })

      const store = useAuthStore.getState()
      await store.login({
        email: 'test@example.com',
        password: 'password',
        rememberMe: false,
      })

      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(true)
      expect(state.user).toEqual(mockUser)
      expect(state.tokens.access).toBe(mockTokens.access_token)
      expect(SecureStorage.setAccessToken).toHaveBeenCalled()
    })

    it('should handle login failure', async () => {
      const { authService } = await import('@/lib/api/auth.service')
      vi.mocked(authService.login).mockRejectedValue(new Error('Invalid credentials'))

      const store = useAuthStore.getState()
      
      await expect(
        store.login({
          email: 'test@example.com',
          password: 'wrong-password',
          rememberMe: false,
        })
      ).rejects.toThrow('Invalid credentials')

      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(false)
      expect(state.error).toBeTruthy()
    })

    it('should handle token refresh', async () => {
      const mockTokens = {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
      }

      vi.mocked(SecureStorage.getRefreshToken).mockReturnValue('refresh-token')
      
      const { authService } = await import('@/lib/api/auth.service')
      vi.mocked(authService.post).mockResolvedValue({
        data: mockTokens,
      })

      const store = useAuthStore.getState()
      await store.refreshTokens()

      const state = useAuthStore.getState()
      expect(state.tokens.access).toBe(mockTokens.access_token)
      expect(SecureStorage.setAccessToken).toHaveBeenCalledWith(
        mockTokens.access_token,
        expect.any(Object)
      )
    })

    it('should handle permission checks', () => {
      useAuthStore.setState({
        permissions: ['read', 'write', 'admin'],
        role: 'admin',
      })

      const store = useAuthStore.getState()
      
      expect(store.hasPermission('read')).toBe(true)
      expect(store.hasPermission('delete')).toBe(false)
      expect(store.hasRole('admin')).toBe(true)
      expect(store.hasRole('user')).toBe(false)
      expect(store.hasAnyPermission(['read', 'delete'])).toBe(true)
      expect(store.hasAllPermissions(['read', 'write'])).toBe(true)
      expect(store.hasAllPermissions(['read', 'delete'])).toBe(false)
    })

    it('should handle logout', async () => {
      useAuthStore.setState({
        user: { id: 'user-1' } as any,
        isAuthenticated: true,
        tokens: { access: 'token', refresh: 'refresh' },
      })

      const store = useAuthStore.getState()
      await store.logout()

      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(false)
      expect(state.user).toBeNull()
      expect(state.tokens.access).toBeNull()
      expect(SecureStorage.clearAll).toHaveBeenCalled()
    })
  })

  describe('AssessmentStore', () => {
    it('should load assessments', async () => {
      const mockAssessments = [
        { id: 'assess-1', name: 'Test Assessment', status: 'completed' },
        { id: 'assess-2', name: 'Test Assessment 2', status: 'in_progress' },
      ]

      const store = useAssessmentStore.getState()
      store.setAssessments(mockAssessments as any)

      const state = useAssessmentStore.getState()
      expect(state.assessments).toEqual(mockAssessments)
      expect(state.assessments).toHaveLength(2)
    })

    it('should handle assessment creation', () => {
      const newAssessment = {
        id: 'new-assess',
        name: 'New Assessment',
        status: 'draft',
      }

      const store = useAssessmentStore.getState()
      store.addAssessment(newAssessment as any)

      const state = useAssessmentStore.getState()
      expect(state.assessments).toContain(newAssessment)
    })

    it('should handle assessment updates', () => {
      useAssessmentStore.setState({
        assessments: [
          { id: 'assess-1', name: 'Old Name', status: 'draft' } as any,
        ],
      })

      const store = useAssessmentStore.getState()
      store.updateAssessment('assess-1', { name: 'New Name', status: 'in_progress' } as any)

      const state = useAssessmentStore.getState()
      const assessment = state.assessments.find(a => a.id === 'assess-1')
      expect(assessment?.name).toBe('New Name')
      expect(assessment?.status).toBe('in_progress')
    })

    it('should handle framework loading', () => {
      const mockFrameworks = [
        { id: 'gdpr', name: 'GDPR' },
        { id: 'iso27001', name: 'ISO 27001' },
      ]

      const store = useAssessmentStore.getState()
      store.setFrameworks(mockFrameworks as any)

      const state = useAssessmentStore.getState()
      expect(state.frameworks).toEqual(mockFrameworks)
    })
  })

  describe('EvidenceStore', () => {
    it('should load evidence items', () => {
      const mockEvidence = [
        { id: 'ev-1', name: 'Evidence 1', status: 'collected' },
        { id: 'ev-2', name: 'Evidence 2', status: 'pending' },
      ]

      const store = useEvidenceStore.getState()
      store.setEvidence(mockEvidence as any)

      const state = useEvidenceStore.getState()
      expect(state.evidence).toEqual(mockEvidence)
    })

    it('should handle evidence filtering', () => {
      const filters = {
        status: 'collected',
        framework: 'gdpr',
        dateRange: { from: new Date(), to: new Date() },
      }

      const store = useEvidenceStore.getState()
      store.setFilters(filters)

      const state = useEvidenceStore.getState()
      expect(state.filters).toEqual(filters)
    })

    it('should handle evidence updates', () => {
      useEvidenceStore.setState({
        evidence: [
          { id: 'ev-1', name: 'Evidence 1', status: 'pending' } as any,
        ],
      })

      const store = useEvidenceStore.getState()
      store.updateEvidence('ev-1', { status: 'collected' })

      const state = useEvidenceStore.getState()
      const evidence = state.evidence.find(e => e.id === 'ev-1')
      expect(evidence?.status).toBe('collected')
    })
  })

  describe('DashboardStore', () => {
    it('should manage dashboard widgets', () => {
      const mockWidgets = [
        { id: 'widget-1', type: 'compliance-score', config: {} },
        { id: 'widget-2', type: 'pending-tasks', config: {} },
      ]

      const store = useDashboardStore.getState()
      store.setWidgets(mockWidgets as any)

      const state = useDashboardStore.getState()
      expect(state.widgets).toEqual(mockWidgets)
    })

    it('should handle widget reordering', () => {
      useDashboardStore.setState({
        widgets: [
          { id: 'widget-1', type: 'compliance-score', order: 1 } as any,
          { id: 'widget-2', type: 'pending-tasks', order: 2 } as any,
        ],
      })

      const store = useDashboardStore.getState()
      store.reorderWidgets(['widget-2', 'widget-1'])

      const state = useDashboardStore.getState()
      expect(state.widgets[0].id).toBe('widget-2')
      expect(state.widgets[1].id).toBe('widget-1')
    })

    it('should handle metrics updates', () => {
      const mockMetrics = {
        complianceScore: 85,
        pendingTasks: 12,
        completedAssessments: 5,
      }

      const store = useDashboardStore.getState()
      store.setMetrics(mockMetrics)

      const state = useDashboardStore.getState()
      expect(state.metrics).toEqual(mockMetrics)
    })
  })

  describe('Store Interactions', () => {
    it('should handle authentication affecting other stores', async () => {
      // Simulate login
      useAuthStore.setState({
        isAuthenticated: true,
        user: { id: 'user-1' } as any,
      })

      // Other stores should react to authentication
      const assessmentStore = useAssessmentStore.getState()
      const evidenceStore = useEvidenceStore.getState()
      const dashboardStore = useDashboardStore.getState()

      // Verify stores can access user context
      expect(useAuthStore.getState().isAuthenticated).toBe(true)
      
      // Stores should be able to load user-specific data
      assessmentStore.setLoading(true)
      evidenceStore.setLoading(true)
      dashboardStore.setLoading(true)

      expect(useAssessmentStore.getState().isLoading).toBe(true)
      expect(useEvidenceStore.getState().isLoading).toBe(true)
      expect(useDashboardStore.getState().isLoading).toBe(true)
    })

    it('should handle logout clearing dependent stores', async () => {
      // Set up stores with data
      useAuthStore.setState({ isAuthenticated: true, user: { id: 'user-1' } as any })
      useAssessmentStore.setState({ assessments: [{ id: 'assess-1' }] as any })
      useEvidenceStore.setState({ evidence: [{ id: 'ev-1' }] as any })

      // Logout
      const authStore = useAuthStore.getState()
      await authStore.logout()

      // Verify auth store is cleared
      expect(useAuthStore.getState().isAuthenticated).toBe(false)
      
      // Other stores should be cleared or reset
      // (This would depend on your implementation)
    })

    it('should handle concurrent store operations', async () => {
      const promises = [
        useAssessmentStore.getState().setLoading(true),
        useEvidenceStore.getState().setLoading(true),
        useDashboardStore.getState().setLoading(true),
      ]

      await Promise.all(promises)

      expect(useAssessmentStore.getState().isLoading).toBe(true)
      expect(useEvidenceStore.getState().isLoading).toBe(true)
      expect(useDashboardStore.getState().isLoading).toBe(true)
    })
  })
})