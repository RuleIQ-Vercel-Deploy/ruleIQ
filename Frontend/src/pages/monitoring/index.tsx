import { Routes, Route } from "react-router-dom"
import { MonitoringDashboard } from "./monitoring-dashboard"
import { UserActivity } from "./user-activity"
import { ErrorMonitoring } from "./error-monitoring"
import { AlertManagement } from "./alert-management"
import { AuditLogs } from "./audit-logs"

export function MonitoringRoutes() {
  return (
    <Routes>
      <Route index element={<MonitoringDashboard />} />
      <Route path="activity" element={<UserActivity />} />
      <Route path="errors" element={<ErrorMonitoring />} />
      <Route path="alerts" element={<AlertManagement />} />
      <Route path="audit" element={<AuditLogs />} />
    </Routes>
  )
}

export default MonitoringRoutes
