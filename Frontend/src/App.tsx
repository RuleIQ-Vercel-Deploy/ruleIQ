import type React from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { Toaster } from "@/components/ui/toaster"
import { MainAppLayout } from "@/components/layout/main-app-layout"
import { ErrorBoundary } from "@/components/layout/error-boundary"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { SessionManager } from "@/components/auth/session-manager"
import { LoginForm } from "@/components/auth/login-form"
import { RegisterForm } from "@/components/auth/register-form"
import { PasswordResetForm } from "@/components/auth/password-reset-form"
import { LandingPage } from "@/pages/landing"
import { useAuthStore } from "@/store/auth-store"
import { Suspense, lazy } from "react"
import { LoadingLayout } from "@/components/layout/loading-layout"
import { PERMISSIONS, ROLES } from "@/components/auth/route-permissions"
import { ErrorProvider } from "@/contexts/error-context"
import { NetworkStatusProvider } from "@/hooks/use-network-status"
import { PerformanceProvider } from "@/hooks/use-performance"

// Lazy load major route components for code splitting
const EnhancedDashboard = lazy(() =>
  import("@/pages/enhanced-dashboard").then((module) => ({ default: module.EnhancedDashboard })),
)
const BusinessProfilesRoutes = lazy(() =>
  import("@/pages/business-profiles").then((module) => ({ default: module.BusinessProfilesRoutes })),
)
const EvidenceRoutes = lazy(() => import("@/pages/evidence").then((module) => ({ default: module.EvidenceRoutes })))
const AssessmentsRoutes = lazy(() =>
  import("@/pages/assessments").then((module) => ({ default: module.AssessmentsRoutes })),
)
const ChatRoutes = lazy(() => import("@/pages/chat").then((module) => ({ default: module.ChatRoutes })))
const ReportsRoutes = lazy(() => import("@/pages/reports").then((module) => ({ default: module.ReportsRoutes })))
const IntegrationsRoutes = lazy(() =>
  import("@/pages/integrations").then((module) => ({ default: module.IntegrationsRoutes })),
)
const MonitoringRoutes = lazy(() =>
  import("@/pages/monitoring").then((module) => ({ default: module.MonitoringRoutes })),
)

// Lazy load less frequently used components
const TeamManagement = lazy(() =>
  import("@/pages/team-management").then((module) => ({ default: module.TeamManagement })),
)
const Settings = lazy(() => import("@/pages/settings").then((module) => ({ default: module.Settings })))
const UserProfile = lazy(() => import("@/pages/user-profile").then((module) => ({ default: module.UserProfile })))
const Billing = lazy(() => import("@/pages/billing").then((module) => ({ default: module.Billing })))
const Notifications = lazy(() => import("@/pages/notifications").then((module) => ({ default: module.Notifications })))
const Help = lazy(() => import("@/pages/help").then((module) => ({ default: module.Help })))
const Search = lazy(() => import("@/pages/search").then((module) => ({ default: module.Search })))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    },
  },
})

// Placeholder components for routes not yet implemented
const PlaceholderPage = ({ title }: { title: string }) => (
  <div className="space-y-6">
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{title}</h1>
      <p className="text-gray-600 dark:text-gray-400">This page is coming soon.</p>
    </div>
  </div>
)

// Optimized loading component with better UX
const OptimizedSuspense = ({ children, fallback }: { children: React.ReactNode; fallback?: React.ReactNode }) => (
  <Suspense fallback={fallback || <LoadingLayout />}>{children}</Suspense>
)

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <ErrorProvider>
      <NetworkStatusProvider>
        <PerformanceProvider>
          <ErrorBoundary>
            <QueryClientProvider client={queryClient}>
              <Router>
                <div className="App">
                  <Routes>
                    {/* Public routes */}
                    <Route path="/" element={<LandingPage />} />
                    <Route
                      path="/login"
                      element={isAuthenticated ? <Navigate to="/app/dashboard" replace /> : <LoginForm />}
                    />
                    <Route
                      path="/register"
                      element={isAuthenticated ? <Navigate to="/app/dashboard" replace /> : <RegisterForm />}
                    />
                    <Route
                      path="/reset-password"
                      element={isAuthenticated ? <Navigate to="/app/dashboard" replace /> : <PasswordResetForm />}
                    />

                    {/* Protected routes with main layout */}
                    <Route
                      path="/app/*"
                      element={
                        <ProtectedRoute>
                          <SessionManager>
                            <MainAppLayout />
                          </SessionManager>
                        </ProtectedRoute>
                      }
                    >
                      {/* Dashboard - accessible to all authenticated users */}
                      <Route
                        path="dashboard"
                        element={
                          <OptimizedSuspense>
                            <EnhancedDashboard />
                          </OptimizedSuspense>
                        }
                      />

                      {/* Business Profiles - requires read permission */}
                      <Route
                        path="business-profiles/*"
                        element={
                          <ProtectedRoute requiredPermissions={[PERMISSIONS.BUSINESS_PROFILE_READ]}>
                            <OptimizedSuspense>
                              <BusinessProfilesRoutes />
                            </OptimizedSuspense>
                          </ProtectedRoute>
                        }
                      />

                      {/* Evidence Management - requires read permission */}
                      <Route
                        path="evidence/*"
                        element={
                          <ProtectedRoute requiredPermissions={[PERMISSIONS.EVIDENCE_READ]}>
                            <OptimizedSuspense>
                              <EvidenceRoutes />
                            </OptimizedSuspense>
                          </ProtectedRoute>
                        }
                      />

                      {/* Assessments - requires read permission */}
                      <Route
                        path="assessments/*"
                        element={
                          <ProtectedRoute requiredPermissions={[PERMISSIONS.ASSESSMENT_READ]}>
                            <OptimizedSuspense>
                              <AssessmentsRoutes />
                            </OptimizedSuspense>
                          </ProtectedRoute>
                        }
                      />

                      {/* AI Chat - accessible to all authenticated users */}
                      <Route
                        path="chat/*"
                        element={
                          <OptimizedSuspense>
                            <ChatRoutes />
                          </OptimizedSuspense>
                        }
                      />

                      {/* Reports - requires read permission */}
                      <Route
                        path="reports/*"
                        element={
                          <ProtectedRoute requiredPermissions={[PERMISSIONS.REPORT_READ]}>
                            <OptimizedSuspense>
                              <ReportsRoutes />
                            </OptimizedSuspense>
                          </ProtectedRoute>
                        }
                      />

                      {/* Team Management - requires team read permission */}
                      <Route
                        path="team"
                        element={
                          <ProtectedRoute requiredPermissions={[PERMISSIONS.TEAM_READ]}>
                            <OptimizedSuspense>
                              <TeamManagement />
                            </OptimizedSuspense>
                          </ProtectedRoute>
                        }
                      />

                      {/* Settings - requires admin role or settings permission */}
                      <Route
                        path="settings"
                        element={
                          <ProtectedRoute requiredRole={ROLES.ADMIN}>
                            <OptimizedSuspense>
                              <Settings />
                            </OptimizedSuspense>
                          </ProtectedRoute>
                        }
                      />

                      {/* User Profile - accessible to all authenticated users */}
                      <Route
                        path="profile"
                        element={
                          <OptimizedSuspense>
                            <UserProfile />
                          </OptimizedSuspense>
                        }
                      />

                      {/* Billing - requires admin role */}
                      <Route
                        path="billing"
                        element={
                          <ProtectedRoute requiredRole={ROLES.ADMIN}>
                            <OptimizedSuspense>
                              <Billing />
                            </OptimizedSuspense>
                          </ProtectedRoute>
                        }
                      />

                      {/* Other routes accessible to all authenticated users */}
                      <Route
                        path="notifications"
                        element={
                          <OptimizedSuspense>
                            <Notifications />
                          </OptimizedSuspense>
                        }
                      />
                      <Route
                        path="help"
                        element={
                          <OptimizedSuspense>
                            <Help />
                          </OptimizedSuspense>
                        }
                      />
                      <Route
                        path="search"
                        element={
                          <OptimizedSuspense>
                            <Search />
                          </OptimizedSuspense>
                        }
                      />

                      {/* Integrations - accessible to all authenticated users */}
                      <Route
                        path="integrations/*"
                        element={
                          <OptimizedSuspense>
                            <IntegrationsRoutes />
                          </OptimizedSuspense>
                        }
                      />

                      {/* Monitoring - requires admin role */}
                      <Route
                        path="monitoring/*"
                        element={
                          <ProtectedRoute requiredRole={ROLES.ADMIN}>
                            <OptimizedSuspense>
                              <MonitoringRoutes />
                            </OptimizedSuspense>
                          </ProtectedRoute>
                        }
                      />

                      <Route path="" element={<Navigate to="dashboard" replace />} />
                    </Route>

                    {/* Legacy routes - redirect to new structure */}
                    <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
                    <Route path="/business-profiles" element={<Navigate to="/app/business-profiles" replace />} />
                    <Route path="/evidence" element={<Navigate to="/app/evidence" replace />} />
                    <Route path="/chat" element={<Navigate to="/app/chat" replace />} />
                    <Route path="/reports" element={<Navigate to="/app/reports" replace />} />
                    <Route path="/settings" element={<Navigate to="/app/settings" replace />} />

                    {/* Fallback route */}
                    <Route path="*" element={<Navigate to={isAuthenticated ? "/app/dashboard" : "/"} replace />} />
                  </Routes>
                  <Toaster />
                </div>
              </Router>
            </QueryClientProvider>
          </ErrorBoundary>
        </PerformanceProvider>
      </NetworkStatusProvider>
    </ErrorProvider>
  )
}

export default App
